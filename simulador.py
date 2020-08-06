from collections import deque
from recursos import Recurso
#from tabulate import tabulate

import datetime
import time
import threading

class Simulador:
    def __init__(self, **kwargs):
        self.cola_espera = deque()
        self.cola_terminados = deque()
        self.cola_procesos = deque()
        self.total_recursos_lectura = 0
        self.ciclo = 0
        self.app = None
        self.tiempo_sleep = kwargs.get('tiempo_sleep', 5)
        self.verbose = kwargs.get('verbose', True)
        self.recursos = []
        self.cantidad_bases_de_datos = 2
        for i in range(0, self.cantidad_bases_de_datos):
            self.recursos.append(Recurso(nombre=f'db_{i}'))

    def set_app(self, app):
        #necesitamos tener comunicacion con el proceso grafico para poder refrescar la interfaz en tiempo real
        self.app = app

    def agregar_proceso(self, proceso):
        #agregamos proceso a la cola de espera
        self.cola_espera.append(proceso)

    def restart(self):
        self.cola_terminados.clear()
        self.cola_espera.clear()
        self.cola_procesos.clear()
        self.ciclo = 0

    def log_simulacion(self, txt):
        if self.verbose:
            print(f'[{datetime.datetime.now()}] Simulador -- ciclo {self.ciclo} - {txt}')
            
    def determinar_recurso_disponible(self, proceso):
        self.log_simulacion(f'Determinando recurso disponible del pool de {len(self.recursos)} DB/s ...')
        #de todos los disponibles, devolvemos el que pueda leer/escribir dependiendo del estado de sus mutex.
        #el primero que me devuelva que puede ejecutar, se lo mando
        for recurso in self.recursos:
            ret, msg = recurso.puedo_ejecutar_proceso(proceso)
            if msg in ['OK']:
                self.log_simulacion(f'Primer DB disponible encontrada, {str(recurso)}')
                return recurso, ret, msg
        return None, ret, msg
    
    def print_estado_colas(self):
        self.log_simulacion('Estado de colas: ')
        
        if self.cola_espera:
            self.log_simulacion('==Cola Espera===')
            for proceso in self.cola_espera:
                self.log_simulacion(f'{str(proceso)}')
            
        if self.cola_procesos:
            self.log_simulacion('===Cola Procesos===')
            for proceso in self.cola_procesos:
                self.log_simulacion(f'{str(proceso)}')
         
        if self.cola_terminados:
            self.log_simulacion('==Cola Terminados===')
            for proceso in self.cola_terminados:
                self.log_simulacion(f'{str(proceso)}')
                
        
    def agregar_proceso_terminado(self, proceso):
        self.log_simulacion(f'Proceso {proceso.pid} terminado ...')
        self.cola_terminados.append(proceso)
                
    def lanzar_proceso(self, proceso, recurso):
        x = threading.Thread(target=proceso.realizar_accion, args=(recurso, self))
        x.start()
        return x

    def iniciar(self):
        while True:
            self.log_simulacion('inicio')
            ejecute_un_proceso = False

            #para no complicarnos con procesar de mas, si no tengo nada en la cola de espera y no tengo nada en la cola
            #de ejecucion, duermo el proceso y rompo el loop principal hasta que carguen de afuera mas procesos
            if not self.cola_espera and not self.cola_procesos:
                self.log_simulacion(f'Nada mas que procesar... espero hasta el proximo ciclo [{self.tiempo_sleep}s]')
                self.ciclo += 1
                time.sleep(self.tiempo_sleep)
                continue
            
            
            #############################################################################################################
            #
            #Zona critica: Manejamos dos colas, una de espera que viene de la GUI con la cual insertamos procesos a la 
            #simulacion que esta corriendo, y una cola de procesos que maneja como se van ejecutando los procesos
            #
            #
            #
            #############################################################################################################
            #siempre preguntamos primero por la cola de espera
            if self.cola_espera:            
                self.log_simulacion(f'Hay {len(self.cola_espera)} proceso/s en la cola de espera')
                #caso 1 - si el tiempo de entrada del primer elemento de la cola coincide con el ciclo actual
                if self.cola_espera[0].tiempo_entrada == self.ciclo:
                    
                    #primero lo saco de la cola
                    proceso_actual = self.cola_espera.popleft()
    
                    self.log_simulacion(f'Sale de cola de espera -> {proceso_actual}')
    
                    recurso, puedo_ejecutar, msg = self.determinar_recurso_disponible(proceso_actual)
                    if puedo_ejecutar:
                        self.log_simulacion('Puedo ejecutar proceso actual')
                        self.lanzar_proceso(proceso_actual, recurso)
                    else:
                        self.log_simulacion('No puedo ejecutar actualmente, agrego a cola de procesos')
                        self.log_simulacion(f'Razon: {msg}')
                        self.cola_procesos.append(proceso_actual)
                        
                    ejecute_un_proceso = True
                else:
                    self.log_simulacion('Todavia no puedo ejecutar proceso de la cola de espera')
                    self.log_simulacion(f'PID [{self.cola_espera[0].pid}] T Entrada [{self.cola_espera[0].tiempo_entrada}]')
            else:
                self.log_simulacion('No hay procesos en la cola de espera')
                
            #si no ejecute nada de la cola de espera, paso a revisar la cola de procesos
            if not ejecute_un_proceso:
                if self.cola_procesos:
                    self.log_simulacion(f'Hay {len(self.cola_procesos)} proceso/s esperando que se liberen recursos')
                    self.log_simulacion(f'Cola de procesos pendientes {[p.pid for p in self.cola_procesos]}')
                    recurso, puedo_ejecutar, msg = self.determinar_recurso_disponible(self.cola_procesos[0])
                    if puedo_ejecutar:
                        self.log_simulacion('Puedo ejecutar proceso pendiente')
                        proceso_actual = self.cola_procesos.popleft()
                        self.lanzar_proceso(proceso_actual, recurso)
                    else:
                        self.log_simulacion('Todavia no puedo ejecutar proceso pendiente')
                        self.log_simulacion(f'Razon: {msg}')

            # terminamos el ciclo
            self.log_simulacion('fin')
            self.ciclo += 1

            #refrescamos la pantalla
            #self.app.refrescar_pantalla(self)
            time.sleep(self.tiempo_sleep)



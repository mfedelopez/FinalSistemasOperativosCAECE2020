from collections import deque
import time
from recursos import Recurso
import threading
import datetime

class Simulador:
    def __init__(self, **kwargs):
        self.cola_espera = deque()
        self.cola_salida = deque()
        self.cola_procesos = deque()
        self.total_recursos_lectura = 0
        self.recurso = Recurso()
        self.ciclo = 0
        self.app = None
        self.tiempo_sleep = kwargs.get('tiempo_sleep', 5)
        self.verbose = kwargs.get('verbose', True)

    def set_app(self, app):
        #necesitamos tener comunicacion con el proceso grafico para poder refrescar la interfaz en tiempo real
        self.app = app

    def agregar_proceso(self, proceso):
        #agregamos proceso a la cola de espera
        self.cola_espera.append(proceso)

    def restart(self):
        self.cola_salida.clear()
        self.cola_espera.clear()
        self.cola_procesos.clear()
        self.ciclo = 0

    def log_simulacion(self, txt):
        if self.verbose:
            print(f'[{datetime.datetime.now()}] Simulador -- ciclo {self.ciclo} - {txt}')
            
    def lanzar_proceso(self, proceso):
        x = threading.Thread(target=proceso.realizar_accion, args=(self.recurso,))
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
    
                    if self.recurso.puedo_ejecutar_proceso(proceso_actual):
                        self.log_simulacion('Puedo ejecutar proceso actual')
                        self.lanzar_proceso(proceso_actual)
                    else:
                        self.log_simulacion('No puedo ejecutar actualmente, agrego a cola de procesos')
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
                    if self.recurso.puedo_ejecutar_proceso(self.cola_procesos[0]):
                        self.log_simulacion('Puedo ejecutar proceso pendiente')
                        proceso_actual = self.cola_procesos.popleft()
                        self.lanzar_proceso(proceso_actual)
                    else:
                        self.log_simulacion('Los recursos necesarios todavia no fueron liberados')
                        
                    
                    
                

            # terminamos el ciclo
            self.log_simulacion('fin')
            self.ciclo += 1

            #refrescamos la pantalla
            #self.app.refrescar_pantalla(self)
            time.sleep(self.tiempo_sleep)



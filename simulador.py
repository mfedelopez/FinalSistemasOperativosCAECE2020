from collections import deque
from recursos import Recurso
from tabulate import tabulate

import datetime
import numpy as np
import os
import pandas as pd
import time
import threading

class Simulador:
    def __init__(self, **kwargs):
        self.cola_espera = deque()
        self.cola_terminados = deque()
        self.cola_procesos = deque()
        self.lista_procesos_ejecucion = []
        self.total_recursos_lectura = 0
        self.ciclo = 0
        self.app = None
        self.tiempo_sleep = kwargs.get('tiempo_sleep', 5)
        self.verbose = kwargs.get('verbose', True)
        self.recursos = []
        self.cantidad_bases_de_datos = kwargs.get('cantidad_db',1)
        self.cantidad_recursos = kwargs.get('cantidad_recursos',10000)
        self.loop_metrics_list = []
        self.ciclo_muerto = 0
        for i in range(0, self.cantidad_bases_de_datos):
            self.recursos.append(Recurso(nombre=f'db_{i}',
                                         cantidad_recursos=self.cantidad_recursos))

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
        output_txt = f'[{datetime.datetime.now()}] Simulador -- ciclo {self.ciclo} - {txt}'
        if self.verbose:
            print(output_txt)
            
        with open('output_sim.txt', 'a') as f:
            f.writelines(output_txt + '\n')
        
    def init_loop_vars(self):
        self._start_time_loop = datetime.datetime.now()
        self._estado_cola_espera = len(self.cola_espera)
        self._estado_cola_procesos = len(self.cola_procesos)
        self._estado_cola_terminados = len(self.cola_terminados)
                
    
    def generate_loop_metrics(self):
        delta_tiempo = (datetime.datetime.now() - self._start_time_loop).seconds
        estado_cola_espera = self._estado_cola_espera - len(self.cola_espera)
        estado_cola_procesos = self._estado_cola_procesos - len(self.cola_procesos)
        estado_cola_terminados = self._estado_cola_terminados - len(self.cola_terminados)
        
        result = {'delta_tiempo':delta_tiempo,
                  'estado_cola_espera':estado_cola_espera,
                  'estado_cola_procesos':estado_cola_procesos,
                  'estado_cola_terminados':estado_cola_terminados,}
      
        for recurso in self.recursos:
            rec = recurso.to_dict()
            for key, value in rec.items():
                result[f'rec_{key}'] = value
                       
        self.loop_metrics_list.append(result)
    
    def _get_file_summary(self):
        filename = 'simulation_summary.txt'
        if os.path.exists(filename):
            os.remove(filename) #empezamos de cero siempre
        
        return open(filename, 'a')
    
    def log_summary(self):
        f = self._get_file_summary()
        df = pd.DataFrame(self.loop_metrics_list)
        
        f.writelines(f'[{datetime.datetime.now()}] Resumen de la simulacion - ciclo {self.ciclo}\n')
        f.writelines('---------------------------------------------------------------------------------\n')
        f.writelines(f'Cantidad de procesos esperando: {len(self.cola_espera)} \n')
        f.writelines(f'Cantidad de procesos ejecutando: {len(self.lista_procesos_ejecucion)}\n')
        f.writelines(f'Cantidad de procesos esperando recursos: {len(self.cola_procesos)}\n')
        f.writelines(f'Cantidad de procesos terminados: {len(self.cola_terminados)}\n\n')
        
        
        # if self.cola_espera:
        #     f.writelines('procesos en cola de espera: \r\n' ) 
        #     for proc in list(self.cola_espera):
        #         proc_df = pd.DataFrame(proc.to_dict().items())
        #         table = tabulate(proc_df, headers='keys', tablefmt='psql') 
        #         f.writelines(table)
        #         f.writelines('')
        
        dfs = []
        if self.cola_procesos:
            procs_df = pd.DataFrame([proc.to_dict() for proc in list(self.cola_procesos)])
            f.writelines(f'\nProcesos esperando para ser lanzados: \n{procs_df["pid"].values} \r\n' )
            dfs.append(procs_df)
        
        if self.lista_procesos_ejecucion:
            ejecucion_df = pd.DataFrame([proc.to_dict() for proc in self.lista_procesos_ejecucion])
            f.writelines(f'\nProcesos en ejecucion: \n{ejecucion_df["pid"].values} \r\n' )
            data = tabulate(ejecucion_df, headers='keys', tablefmt='psql')
            f.writelines(data)
            dfs.append(ejecucion_df)    
            
        if self.cola_terminados:
            terminados_df = pd.DataFrame([proc.to_dict() for proc in list(self.cola_terminados)])
            f.writelines(f'\nProcesos terminados: \n{terminados_df["pid"].values} \r\n' )
            tiempos_lectura = terminados_df[terminados_df.accion == 'L']["total_tiempo"].values
            tiempo_promedio_lectura = np.average(tiempos_lectura) if len(tiempos_lectura) else np.nan
            
            tiempo_escritura = terminados_df[terminados_df.accion == 'E']["total_tiempo"].values
            tiempo_promedio_escritura = np.average(tiempo_escritura) if len(tiempo_escritura) else np.nan
            
            tiempo_promedio =  terminados_df["total_tiempo"].values
            tiempo_promedio_total = np.average(tiempo_promedio) if len(tiempo_promedio) else np.nan
            tiempo_total = np.sum(tiempo_promedio)
            
            f.writelines(f'Tiempo promedio de ejecucion [t(L)] = {tiempo_promedio_lectura}s \n' +\
                         f'Tiempo promedio de ejecucion [t(E)] = {tiempo_promedio_escritura}s \n'+\
                         f'Tiempo promedio de ejecucion [t(L) + t(E)] = {tiempo_promedio_total}s\n' +\
                         f'Tiempo total ejecutando procesos = {tiempo_total}s \n\n')
                
            data = tabulate(terminados_df,  headers='keys', tablefmt='psql')
            f.writelines(data)
            dfs.append(terminados_df)    
                        
        f.writelines('\n\nTabla de ejecucion de por ciclo \n\n')
        data = tabulate(df, headers='keys', tablefmt='psql')
        f.writelines(data)
        f.close()
        
    def loop_metrics(self):
        '''
        pasos para agregar una metrica del loop:
            1- inicializar contador en init_loop_vars
            2- procesas el contador en generate_loop_metrics
            3- profit

        Returns
        -------
        None.

        '''
        self.log_simulacion(f'generando metricas para el loop [{self.ciclo}]')
        self.generate_loop_metrics()
        self.log_summary()
        
            
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
        self.lista_procesos_ejecucion.remove(proceso)
                        
    def lanzar_proceso(self, proceso, recurso):
        self.lista_procesos_ejecucion.append(proceso)
        x = threading.Thread(target=proceso.realizar_accion, args=(recurso, self))
        x.start()
        return x

    def iniciar(self):
        while True:
            self.log_simulacion('inicio')
            ejecute_un_proceso = False
            proceso_perdido = False
            self.init_loop_vars()

            #para no complicarnos con procesar de mas, si no tengo nada en la cola de espera y no tengo nada en la cola
            #de ejecucion, duermo el proceso y rompo el loop principal hasta que carguen de afuera mas procesos
            if not self.cola_espera and not self.cola_procesos:
                self.log_simulacion(f'Nada mas que procesar... espero hasta el proximo ciclo [{self.tiempo_sleep}s]')
                self.loop_metrics()
                self.ciclo += 1
                time.sleep(self.tiempo_sleep)
                self.ciclo_muerto += 1
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
                self.ciclo_muerto = 0
                self.log_simulacion(f'Hay {len(self.cola_espera)} proceso/s en la cola de espera')
                #caso 1 - si el tiempo de entrada del primer elemento de la cola coincide con el ciclo actual
                procesos_en_t = True
                while procesos_en_t:
                    if self.cola_espera[0].tiempo_entrada == self.ciclo:
                        #primero lo saco de la cola
                        proceso_actual = self.cola_espera.popleft()
                        procesos_en_t = bool(len(self.cola_espera))
        
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
                    elif self.cola_espera[0].tiempo_entrada < self.ciclo:
                        self.log_simulacion('Tiempo de entrada > ciclo, lo paso a la cola de procesos pendientes')
                        proceso_actual = self.cola_espera.popleft()
                        self.cola_procesos.append(proceso_actual) 
                        proceso_perdido = True
                    else:
                        self.log_simulacion('Todavia no puedo ejecutar proceso de la cola de espera')
                        self.log_simulacion(f'PID [{self.cola_espera[0].pid}] T Entrada [{self.cola_espera[0].tiempo_entrada}]')
                        procesos_en_t = False
                else:
                    self.log_simulacion('No hay procesos en la cola de espera')
                
            #si no ejecute nada de la cola de espera, paso a revisar la cola de procesos
            if not ejecute_un_proceso or proceso_perdido:
                if self.cola_procesos:
                    self.ciclo_muerto = 0
                    last = None
                    prioridad = None
                    for proc in self.cola_procesos:
                        if proc.accion in ['E']:
                            self.log_simulacion(f'proximo proceso escritor tiene prioridad')
                            self.log_simulacion(f'{str(proc)}')
                            prioridad = proc
                        last = proc
                    self.log_simulacion(f'Hay {len(self.cola_procesos)} proceso/s esperando que se liberen recursos')
                    self.log_simulacion(f'Cola de procesos pendientes {[p.pid for p in self.cola_procesos]}')
                    recurso, puedo_ejecutar, msg = self.determinar_recurso_disponible(prioridad or last)
                    if puedo_ejecutar:
                        self.log_simulacion('Puedo ejecutar proceso pendiente')
                        proceso_actual = self.cola_procesos.remove(prioridad or last)
                        self.lanzar_proceso(prioridad or last, recurso)
                    else:
                        self.log_simulacion('Todavia no puedo ejecutar proceso pendiente')
                        self.log_simulacion(f'Razon: {msg}')

            # ultimo log: metricas del loop
            self.loop_metrics()

            # terminamos el ciclo
            self.log_simulacion('fin')
            self.ciclo += 1

            #refrescamos la pantalla
            #self.app.refrescar_pantalla(self)
            time.sleep(self.tiempo_sleep)
            
            #con mas de 50 ciclos sin hacer nada frenamos la ejecucion
            if self.ciclo_muerto in [10]:
                self.log_simulacion(f'Simulacion terminada en ciclo {self.ciclo} despues de {10} ciclos sin actividad')
                break
                



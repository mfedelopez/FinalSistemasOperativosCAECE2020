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
        print(f'[{datetime.datetime.now()}] Simulador -- ciclo {self.ciclo} - {txt}')

    def iniciar(self):
        while True:
            self.log_simulacion('inicio')

            #para no complicarnos con procesar de mas, si no tengo nada en la cola de espera y no tengo nada en la cola
            #de ejecucion, duermo el proceso y rompo el loop principal hasta que carguen de afuera mas procesos
            if not self.cola_espera and not self.cola_procesos:
                self.log_simulacion('Nada mas que procesar... espero hasta el proximo ciclo')
                self.ciclo += 1
                time.sleep(self.tiempo_sleep)
                continue

            #caso 1 - si el tiempo de entrada del primer elemento de la cola coincide con el ciclo actual
            if self.cola_espera[0].tiempo_entrada == self.ciclo:
                #primero lo saco de la cola
                proceso_actual = self.cola_espera.popleft()

                self.log_simulacion(f'Sale de cola de espera -> {proceso_actual}')

                if self.recurso.puedo_ejecutar_proceso(proceso_actual):
                    self.log_simulacion('Puedo ejecutar proceso actual')
                    x = threading.Thread(target=proceso_actual.realizar_accion)
                    x.start()
                else:
                    self.cola_procesos.append(proceso_actual)

            # terminamos el ciclo
            self.log_simulacion('fin')
            self.ciclo += 1

            #refrescamos la pantalla
            #self.app.refrescar_pantalla(self)
            time.sleep(self.tiempo_sleep)



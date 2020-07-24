import time
import datetime

class Proceso:
    def __init__(self, **kwargs):
        self.accion = kwargs.get('accion', 'lectura')
        self.tiempo_accion = kwargs.get('tiempo_accion')
        self.tiempo_entrada = kwargs.get('tiempo_entrada')
        self.pid = kwargs.get('pid')
        self.demanda_recursos = kwargs.get('demanda_recursos')

        #necesitamos que esten bien los parametros
        if not (self.accion and self.tiempo_entrada and self.tiempo_accion):
            raise Exception(f'Proceso - Error en parametros al crear proceso'\
                            f'{self.accion, self.tiempo_entrada, self.tiempo_accion}')

    #para hacer mas amigable el debugging
    def __str__(self):
        return f'PID: [{self.pid}] ACCION [{self.accion}] T0 [{self.tiempo_entrada}] TA [{self.tiempo_accion}]'

    def log(self, txt):
        print(f'[{datetime.datetime.now()}] - PID {self.pid} - {txt}')

    def realizar_accion(self):
        self.log('inicio')
        if self.accion in ['Lectura']:
            self.log('Leyendo ...')
            time.sleep(self.tiempo_accion)
            self.log('Termino la lectura')
        else:
            self.log('Escribiendo ...')
            time.sleep(self.tiempo_accion)
            self.log('Termino la escritura')


import threading
class Recurso:
    def __init__(self, **kwargs):
        self.nombre = 'RECURSO'
        self.cantidad_recursos = kwargs.get('cantidad_recursos', 10000)
        self.mutex_interrupcion = kwargs.get('mutex_interrupcion', False) #por default no tenemos ninguna interrupcion
        self.mutex_escritura = kwargs.get('mutex_escritura', False) #por default puedo escribir
        self.cantidad_lecturas = 0

    def puedo_ejecutar_proceso(self, proceso):
        # accion = leer
        if proceso.accion in ['Lectura']:
            #si no hay un lector actualmente y tengo los recursos suficientes, puedo leer
            #cantidad de recursos se cancela hasta nuevo aviso
             if not self.mutex_escritura: #and self.cantidad_recursos - proceso.cantidad_recursos > 0:
                 #self.cantidad_recursos -= proceso.cantidad_recursos
                 self.cantidad_lecturas +=1
                 return True



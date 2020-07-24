import datetime
class Recurso:
    def __init__(self, **kwargs):
        self.nombre = 'RECURSO'
        self.cantidad_recursos = kwargs.get('cantidad_recursos', 10000)
        self.mutex_interrupcion = kwargs.get('mutex_interrupcion', False) #por default no tenemos ninguna interrupcion
        self.mutex_escritura = kwargs.get('mutex_escritura', False) #por default puedo escribir
        self.cantidad_lecturas = 0

    def liberar_recursos(self, demanda_recursos):
        #libero los recursos que habia tomado
        self.cantidad_lecturas -=1
        self.cantidad_recursos += demanda_recursos
    
    def tomar_recursos(self, demanda_recursos):
        #tomo recursos
        self.cantidad_lecturas +=1
        self.cantidad_recursos -= demanda_recursos
        
    def bloquear_mutex(self):
        #bloqueo el semaforo para que no puedan escribir
        self.mutex_escritura = True
        
    def desbloquear_mutex(self):
        #bloqueo el semaforo para que no puedan escribir
        self.mutex_escritura = False
        
    def puedo_ejecutar_proceso(self, proceso):
        # accion = leer
        if proceso.accion in ['Lectura']:
            #si no hay un lector actualmente y tengo los recursos suficientes, puedo leer
            #cantidad de recursos se cancela hasta nuevo aviso
             if not self.mutex_escritura: #and self.cantidad_recursos - proceso.cantidad_recursos > 0:
                 #self.cantidad_recursos -= proceso.cantidad_recursos
                 return True
        elif proceso.accion in ['Escritura']:
            #primero tengo que fijarme que todos los lectores hayan terminado de leer
            if self.cantidad_lecturas:
                #si tengo al menos un lector, el escritor tiene que esperar
                return False
            else:
                #no tengo ningun lector esperando, veo si no hay otro escritor
                if not self.mutex_escritura:
                    #procedo a ejecutar este proceso
                    return True
        else:
            raise Exception(f'RECURSO -> ACCION INDEFINIDA {proceso.accion}')
            



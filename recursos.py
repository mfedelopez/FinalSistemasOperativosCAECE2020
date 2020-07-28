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
        
        #desbloqueo el mutex de interrupcion asi dejan de encolarse procesos
        self.mutex_interrupcion = False
        
    def determinar_error_lectura(self, proceso):
        #funcion que me devuelve el mensaje de error para mostrar por consola
        error = ''
        if self.mutex_escritura:
            error += 'mutex de escritura activado '
             
        if not self.cantidad_recursos - proceso.demanda_recursos > 0:
            error += 'no tengo recursos disponibles '
             
        if self.mutex_interrupcion:
            error += 'activada la interrupcion '
                          
        return error if error else "ERROR INDEFINIDO"
    
    def determinar_error_escritura(self):
        #funcion que me devuelve el mensaje de error para mostrar por consola
        error = ''
        
        if self.cantidad_lecturas:
            error += 'todavia hay procesos leyendo '
            self.mutex_interrupcion = True
            
        if self.mutex_escritura:
            error += 'todavia hay un proceso escribiendo '
                          
#        if self.mutex_interrupcion:
#            error += 'interrupcion activa'
        return error if error else "ERROR INDEFINIDO"     
        
    def puedo_ejecutar_proceso(self, proceso):
        # accion = leer
        if proceso.accion in ['Lectura']:
             #condiciones para poder ejecutar un proceso lector:
             #1-no hay otro escritor ejecutandose actualmente (mutex_lectura)
             #2-tengo los recursos que necesito
             #3-no hay un escritor esperando (esos tienen mas prioridad)
             if not self.mutex_escritura and self.cantidad_recursos - proceso.demanda_recursos > 0 and not self.mutex_interrupcion:
                 return True, 'OK'
             else:
                 #enumeramos los errores que pueden llegar a darse, para poder logear mas lindo
                 error = self.determinar_error_lectura(proceso)
                 return False, f'{error}'
        elif proceso.accion in ['Escritura']:
            #condiciones para poder ejecutar un proceso escritor:
            #1-no hay otro escritor esperando (mutex_interrupcion)
            #2-no hay lectores ejecutandose actualmente
            #3-no hay otro escritor ejecutandose actualmente (mutex_lectura)
            if not self.mutex_escritura and not self.cantidad_lecturas:# and not self.mutex_interrupcion:
                return True, 'OK'
            else:
                #enumeramos los errores que pueden llegar a darse para mejor logeo
                error = self.determinar_error_escritura()
                return False, f'{error}'
        else:
            raise Exception(f'RECURSO -> ACCION INDEFINIDA {proceso.accion}')
            



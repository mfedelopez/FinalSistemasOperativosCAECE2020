from simulador import Simulador
from procesos import Proceso

class App:
    def __init__(self):
        self.mutex = 0
        self.simulador = None

    def set_simulador(self, sim):
        self.simulador = sim

    def refrescar_pantalla(self, simulador):
        return

    def main(self):
        #seteo el simulador
        self.set_simulador(Simulador())

        #comienzo la simulacion
        self.simulador.iniciar()

    def agregar_procesos(self, procesos):
        for proceso in procesos:
            self.simulador.agregar_proceso(proceso)

if __name__ == '__main__':
    #para construir
    
    #Para construir procesos:
    
    
    app = App()
    app.set_simulador(Simulador())
    
    #si todos tienen el mismo tiempo de entrada, se inserta en la cola con el orden dado
    app.agregar_procesos([
            Proceso(accion='Lectura',   tiempo_accion=10,  tiempo_entrada=1, pid=100),
            Proceso(accion='Lectura',   tiempo_accion=10,  tiempo_entrada=2, pid=101),
            Proceso(accion='Lectura',   tiempo_accion=10,  tiempo_entrada=3, pid=102),
            Proceso(accion='Escritura', tiempo_accion=25,  tiempo_entrada=4, pid=550),
            Proceso(accion='Lectura',   tiempo_accion=20,  tiempo_entrada=5, pid=104),
            Proceso(accion='Escritura', tiempo_accion=25,  tiempo_entrada=6, pid=551),])
    app.simulador.iniciar()
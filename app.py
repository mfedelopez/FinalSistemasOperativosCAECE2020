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
    app = App()
    app.set_simulador(Simulador())
    app.agregar_procesos([
            Proceso(accion='Escritura', tiempo_accion=25, tiempo_entrada=1, pid=1),
            Proceso(accion='Lectura', tiempo_accion=1, tiempo_entrada=2, pid=2),])
    app.simulador.iniciar()
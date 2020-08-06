import datetime
import random
import threading

from procesos import Proceso
from simulador import Simulador

class App:
    def __init__(self):
        self.mutex = 0
        self.simulador = None
        self.interactiva = True
        self.multithread = True #si lo ejecuto multithread para tener la consola interactiva pierdo visibilidad de los procesos de 2do nivel
        self.lista = False
        self.debug_cmd = False
        self.verbose = True
        self.COMANDOS_DESCRIPCION = {'AGREGAR PROCESO': ': Comando para agregar procesos a la cola de espera de la simulacion',
                                     #'RESET': 'Reseta la simulacion',
                                     #'FIN'  : 'Terminar la simulacion',
                                     'EXIT' : 'Salir del proceso',
                                     'LISTO': 'Terminar la carga de procesos en la simulacion',
                                     'ESTADO': 'Revisar estados de las colas y la simulacion'}
                                     
        self.PROCESOS_DESCRIPCION = {'accion': '"L/E" - Tipo de proceso - Lectura o Escritura)',
                                     'tiempo_accion': 'Cantidad de segundos que va a retener un recurso un proceso',
                                     'tiempo_entrada': 'Tiempo (ciclo) en el que el proceso entra a la cola de espera. Si no es definido, es T+1 del ultimo proceso de la cola',
                                     'pid': 'id del proceso, si no es ninguno se le asigna uno random' }

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
            
    def imprimir_comandos(self):
        self.log_consola('Comandos: ')
        for comando, descripcion in self.COMANDOS_DESCRIPCION.items():
            self.log_consola(f'{comando}: {descripcion}')
            
    def log_consola(self, txt):
        output_txt = f'[{datetime.datetime.now()}] Aplicacion -- {txt}'
        if self.verbose:
            print(output_txt)
            
        with open(f'output_sim.txt', 'a') as f:
            f.write(output_txt + '\n')
            
    
    def consola_interactiva(self):
        self.log_consola("Iniciando consola interactiva ...")
        primer_proceso = True
        procesos_a_ingresar = []
        proc = None
        
        self.imprimir_comandos()
        
        cmd = input().upper()
        self.log_consola(f'{"CMD: "+cmd if self.debug_cmd else ""}')
        while not cmd in ['FIN', 'LISTO']:
            if cmd in ['AGREGAR PROCESO']:
                #para evitar saturar la consola, solamente damos las instrucciones la primera vez
                if primer_proceso:
                    self.log_consola('Formato:')
                    for pr, des in self.PROCESOS_DESCRIPCION.items():
                        self.log_consola(f'{pr}: {des}')
                            
                    self.log_consola('Ingresar separando con comas ...')
                    primer_proceso = False
                    input_usuario = input()
                    
                while input_usuario:
                    #no muestren esto en mi laburo porque me echan
                    args = {}
                    args['accion']         = input_usuario.split(',')[0].upper()
                    args['tiempo_accion']  = int(input_usuario.split(',')[1])
#                    if(len(input_usuario.split(','))) == 3:
                    args['tiempo_entrada'] = int(input_usuario.split(',')[2])
#                    elif proc:
#                        args['tiempo_entrada'] = proc.tiempo_entrada + 1
#                    else:
#                        args['tiempo_entrada'] = 1
                        
#                    if(len(input_usuario.split(','))) == 4:
                    args['pid'] = int(input_usuario.split(',')[3])
#                    else:
#                        args['pid'] = random.randint(0, 10000)
                        
                                            
                    proc = Proceso(**args)
                    
                    procesos_a_ingresar.append(proc)
                    
                    self.log_consola(f'Se ha ingresado correctamente proceso pid: {proc.pid} ...')
                    self.log_consola(f'Ingrese siguiente proceso a continuacion o enter para terminar de cargar procesos ...')
                
                    input_usuario = input()

            
            self.imprimir_comandos()
            cmd = input()
                        
        if cmd in ['EXIT']:
            error_msg = 'Comando EXIT - Terminando proceso ...'
        
        if cmd in ['LISTO']:
            self.log_consola('Se terminaron de cargar los procesos')
        
        if procesos_a_ingresar:
            self.log_consola(f'Finaliza consola interactiva - {len(procesos_a_ingresar)} proceso/s a ingresar ...')
            self.log_consola('Detalle de procesos a ingresar: ')
            self.log_consola('===================================================================================')
            for proc in procesos_a_ingresar:
                self.log_consola(f'{proc}')
            self.log_consola('===================================================================================')
            self.log_consola('La aplicacion esta lista para empezar ...')
            self.lista = True
            return procesos_a_ingresar
        
        elif error_msg:
            self.lista = False
            return error_msg
        
    def input_simulacion_corriendo(self):
        
        cmd = input.upper()
        while not cmd in ['FIN', 'LISTO']:
            if cmd in ['EXIT']:
                return False
        self.log_consola('aca iria la consola de arriba pero solo una vez')
        
    
        

if __name__ == '__main__':
    #inicializacion
    app = App()
    app.set_simulador(Simulador())
    
    #ingreso de procesos por comando o con ejemplo default
    if app.interactiva:
        output = app.consola_interactiva()
        
        #si devuelvo una lista es porque insertamos procesos
        if isinstance(output, list):
            app.agregar_procesos(output)
        elif isinstance(output, str):
            app.log_consola(f'Error en consola interactiva, razon: {output}')
        else:
            app.log_consola(f'')
    else:
        #inicializacion default para testear rapido    
        app.agregar_procesos([
            Proceso(accion='L', tiempo_accion=10,  tiempo_entrada=1, pid=100),
            Proceso(accion='L', tiempo_accion=10,  tiempo_entrada=2, pid=101),
            Proceso(accion='L', tiempo_accion=10,  tiempo_entrada=3, pid=102),
            Proceso(accion='E', tiempo_accion=25,  tiempo_entrada=4, pid=550),
            Proceso(accion='L', tiempo_accion=20,  tiempo_entrada=5, pid=104),
            Proceso(accion='E', tiempo_accion=25,  tiempo_entrada=6, pid=551),])

    #para poder simular la consola interactiva, si o si tengo que correr en multithread
    #sino el while(True) del simulador bloquea el input
    if app.lista:
        if app.multithread:
            app.log_consola('Iniciando simulacion en modo multithreading (simulacion en vivo)')
            x = threading.Thread(target=app.simulador.iniciar)   
            x.start()
        else:
            #necesario para debugging
            print('iniciando sin multithreading')
            app.simulador.iniciar()
    
    #input por consola de procesos en una simulacion corriendo
    #lo deshabilito para probar agregando procesos interactivamente y 
    #obtener funciones del simulador por iPython
#    if app.interactiva:
#        if app.input_simulacion_corriendo():
#        else:
#            x.
    
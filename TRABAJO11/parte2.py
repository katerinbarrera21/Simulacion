from math import trunc
from simpy.rt import RealtimeEnvironment
import PIL.Image
import PIL.ImageTk

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER


import collections
import random
import simpy
from turtle import color
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




VELOCIDAD_LLEGADA = 42
NUM_BOLETO = 50
TIEMPO_SIMULACION = 120




boletos_vendidos = {}

def ventaBoletos(env, num_boletos, pelicula, teatro):
  with teatro.contador.request() as turno:
    resultado = yield turno | teatro.sold_out[pelicula]
    if turno not in resultado:
      teatro.num_renegados[pelicula] += 1
      return
    if teatro.num_boletos[pelicula] < num_boletos:
      yield env.timeout(0.5) 
      return
    else:
        if pelicula in list(boletos_vendidos.keys()):
            a = boletos_vendidos[pelicula]
            a.append(num_boletos)
            boletos_vendidos[pelicula] = a
        else:
            boletos_vendidos[pelicula] = [num_boletos]
    teatro.num_boletos[pelicula] -= num_boletos
    if teatro.num_boletos[pelicula] < 2:
      teatro.sold_out[pelicula].succeed()
      teatro.tiempo_agotado[pelicula] = env.now
      teatro.num_boletos[pelicula] = 0
    yield env.timeout(1)


def llegadaClientes(env, teatro):
  while True:
    yield env.timeout(random.expovariate(1/0.5))
    pelicula = random.choices(teatro.peliculas, teatro.probabilidad, k=1)
    num_boletos = random.randint(1, 6)
    if teatro.num_boletos[pelicula[0]]:
      env.process(ventaBoletos(env, num_boletos, pelicula[0], teatro))


Teatro = collections.namedtuple('Teatro', 'contador, peliculas, probabilidad, num_boletos, sold_out, tiempo_agotado, num_renegados')

print('Teatro Carlos Crespi - UPS')
env = simpy.Environment()

contador = simpy.Resource(env,capacity=1)
peliculas = ['Conjuro 3', 'Rapidos y Furiosos 10', 'Pulp Fictions']
probabilidad=[0.1, 0.3, 0.6]
num_boletos = {pelicula: NUM_BOLETO for pelicula in peliculas}
sold_out = {pelicula: env.event() for pelicula in peliculas}
tiempo_agotado = {pelicula: None for pelicula in peliculas}
num_renegados = {pelicula: 0 for pelicula in peliculas}

teatro = Teatro(contador, peliculas, probabilidad, num_boletos, sold_out, tiempo_agotado, num_renegados)
env.process(llegadaClientes(env, teatro))
env.run(until=TIEMPO_SIMULACION)

def generate_chart(teatro):
    label = list(teatro.peliculas)
    values = []

    for pelicula in teatro.peliculas:
        values.append(teatro.tiempo_agotado[pelicula])

    plt.figure(dpi=300)
    plt.bar(range(len(label)), values, align='center', tick_label = label)
    plt.title(f'TIEMPO PARA QUE SE AGOTEN LAS PELICULAS EN EL TEATRO')
    plt.xlabel('PELICULAS')
    plt.ylabel('TIEMPO')
    # plt.show()
    plt.savefig('PELICULAS_AGOTADAS.png')

generate_chart(teatro)

doc = SimpleDocTemplate("REPORTE_TEATRO.pdf",
                        pagesize = A4,
                        rightMargin = 72,
                        leftMargin = 72,
                        topMargin = 72,
                        bottomMargin = 72)

# Se agregan los elementos
content = []



# Título
content.append(Paragraph('TEATRO CARLOS CRESPI'))
content.append(Spacer(1, 50))


content.append(Paragraph('REPORTE POR PELICULA'))
content.append(Spacer(1, 15))




# Analisis y resultados
for pelicula in peliculas:
  if teatro.sold_out[pelicula]:
    print('Pelicula: %s se agoto en el tiempo %.1f despues de salir a la venta' %(pelicula, teatro.tiempo_agotado[pelicula]))
    print('Numero de personas que salieron de la fila/renegados %s' %teatro.num_renegados[pelicula])
    content.append(Paragraph('Pelicula: %s se agoto en el tiempo %.1f despues de salir a la venta' %(pelicula, teatro.tiempo_agotado[pelicula])))
    content.append(Paragraph('Numero de personas que salieron de la fila/renegados %s' %teatro.num_renegados[pelicula]))

content.append(Spacer(1, 15))
content.append(Paragraph('Venta de boletos por pelicula: '))
content.append(Paragraph('Pelicula: %s _'%(boletos_vendidos)))
content.append(Spacer(1, 15))
content.append(Paragraph('GRÁFICA TIEMPO DE BOLETOS AGOTADOS POR PELICULA: '))
img_name = 'PELICULAS_AGOTADAS.png'
img = Image(img_name, 3*inch, 2*inch)
content.append(img)

doc.build(content)

class ClockAndData: 
    def __init__(self, canvas, peliculas, y1, y2, y3, time): 
        self.y1 = y1
        self.y2 = y2
        self.y3 = y3
        self.peliculas = peliculas
        self.canvas = canvas
        self.step_acum=0
        self.step_x1=[0]
        self.step_y1=[0]
        self.step_x2=[0]
        self.step_y2=[0]
        self.step_x3=[0]
        self.step_y3=[0]
        data_plot.draw()
        self.canvas.update() 

    def tick(self, y1, y2, y3, time): 

        a1.cla()

        self.step_x1.append(time)
        self.step_y1.append(y1)

        self.step_x2.append(time)
        self.step_y2.append(y2)

        self.step_x3.append(time)
        self.step_y3.append(y3)

        a1.set_title("CONJURO 3")
        a1.set_xlabel("--TIEMPO DE VENTA--")
        a1.set_ylabel("--BOLETOS VENDIDOS--")
        a1.step(self.step_x1, self.step_y1, color='yellow')
        a1.legend(['CONJURO 3'])

        a2.set_title("RAPIDOS Y FURIOSOS 10")
        a2.set_xlabel("--TIEMPO DE VENTA--")
        a2.set_ylabel("--BOLETOS VENDIDOS--")
        a2.step(self.step_x2, self.step_y2, color='green')
        a2.legend(['RAPIDOS Y FURIOSOS 10'])

        a3.set_title("PULP FICTIONS")
        a3.set_xlabel("--TIEMPO DE VENTA--")
        a3.set_ylabel("--BOLETOS VENDIDOS--")
        a3.step(self.step_x3, self.step_y3, color='blue')
        a3.legend(['PULP FICTIONS'])

        data_plot.draw()
        self.canvas.update() 
        # Re-draw the the clock and data fields on the canvas. Also update the Matplotlib charts. 

main = tk.Tk()
main.title("BOLETERIA TEATRO CARLOS CRESPI")

top_frame = tk.Frame(main)

canvas = tk.Canvas(main, width = 1300, height = 1)
canvas.pack(side=tk.BOTTOM, expand = False)

f = plt.Figure()

a1=f.add_subplot(1,3,1)
a1.plot()

a2=f.add_subplot(1,3,2)
a2.plot()

a3=f.add_subplot(1,3,3)
a3.plot()

data_plot = FigureCanvasTkAgg(f, master=main)
data_plot.get_tk_widget().config(height = 400)
data_plot.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

canvas.pack()

clock = ClockAndData(canvas, peliculas, 0, 0, 0, 0) 

def create_clock(env):
    i=0

    while True: 
        
        yield env.timeout(random.expovariate(1/0.5))
        
        try:
            clock.tick(boletos_vendidos['Conjuro 3'][i], boletos_vendidos['Rapidos y Furiosos 10'][i], boletos_vendidos['Pulp Fictions'][i], env.now)
            i+=1
        except:
            break            

env = simpy.Environment()
env.process(create_clock(env)) 
env.run(until = TIEMPO_SIMULACION)

main.mainloop()
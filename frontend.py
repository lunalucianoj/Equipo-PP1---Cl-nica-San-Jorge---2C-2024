# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:52:27 2024

@author: Pablo

Front end para la visualizacion de graficos realizado para el area de RRHH
de la Clinica San Jorge (Ushuaia)
"""
# %% Importaciones
import graficos
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import utils
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
from database_setup import crear_db

# %% Graficos institucionales

color_fondo = 'RoyalBlue4'  # Azul similar al de la clinica
logo = 'Logo_clinica_san_jorge_chico.png'



# %% Ventana principal

class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configurar la ventana principal
        self.state('zoomed')  # ventana maximizada
        self.title('Análisis de ausencias Clínica San Jorge')
        self['bg'] = color_fondo
        try:
            self.set_icon()
        except:
            pass

        # Crear el menu para agregar bases de datos
        self.create_menu()

        # Marco para los graficos
        self.fr_graficos = tk.Frame(self, bg=color_fondo, height=600)
        self.fr_graficos.pack(side="top", fill="x")
        # Indicar que falta base de datos
        self.la_falta_excel = tk.Label(
            self.fr_graficos, text='Por favor cargue la tabla de Excel con' +
                                   ' los certificados')
        self.cartel_area_graf()


        # Marco para los seleccionadores
        self.fr_selec = tk.Frame(self, bg = color_fondo, height=400)
        self.fr_selec.pack(side="bottom", fill="x")

        # Marcos para los menus de seleccion
        ''' 4 menus consecutivos (0 a 3) de izquierda a derecha.
        El menu 2 solo aparece si es llamado del menu 1 y asi'''
        self.fr_selec.columnconfigure((0, 1, 2, 3), weight=1)
        self.fr_selec_0 = tk.Frame(self.fr_selec,bg = color_fondo, height=400)
        self.fr_selec_1 = tk.Frame(self.fr_selec, bg = color_fondo, height=400)
        self.fr_selec_2 = tk.Frame(self.fr_selec, bg = color_fondo, height=400)
        self.fr_selec_3 = tk.Frame(self.fr_selec, bg = color_fondo, height=400)
        self.fr_selec_0.grid(row=0, column=0, sticky="nsew")
        self.fr_selec_1.grid(row=0, column=1, sticky="nsew")
        self.fr_selec_2.grid(row=0, column=2, sticky="nsew")
        self.fr_selec_3.grid(row=0, column=3, sticky="nsew")

        # Menues de seleccion
        self.selec_tipo_graf()
        self.ver_selec_tipo_graf(1)
        self.selec_frec_graf()

    # %% Menus de radio buttom

    def selec_tipo_graf(self):
        # Frame 0 (izquierda)
        self.fr_selec_0b = tk.Frame(self.fr_selec_0)
        tex_1 = 'Seleccione el gráfico que desea:'
        self.lab_fr0 = tk.Label(self.fr_selec_0b, text=tex_1)
        self.lab_fr0.grid(row=0, column=0, sticky="w")

        self.var_fr0 = tk.IntVar()
        self.rb0_fr0 = tk.Radiobutton(self.fr_selec_0b,
                                      text='Ausencias totales',
                                      variable=self.var_fr0, value=0,
                                      command=self.distribuidor_frame_0)
        self.rb1_fr0 = tk.Radiobutton(self.fr_selec_0b,
                                      text='Ausencias controlables' +
                                      ' vs no controlables',
                                      variable=self.var_fr0, value=1,
                                      command=self.distribuidor_frame_0)
        self.rb2_fr0 = tk.Radiobutton(self.fr_selec_0b, text='Ausencias' +
                                      ' justificadas vs injustificadas',
                                      variable=self.var_fr0, value=2,
                                      command=self.distribuidor_frame_0)
        self.rb3_fr0 = tk.Radiobutton(self.fr_selec_0b, text='Duración del' +
                                      ' ausentismo',
                                      variable=self.var_fr0, value=3,
                                      command=self.distribuidor_frame_0)
        self.rb0_fr0.grid(row=1, column=0, sticky="w")
        self.rb1_fr0.grid(row=2, column=0, sticky="w")
        self.rb2_fr0.grid(row=3, column=0, sticky="w")
        self.rb3_fr0.grid(row=4, column=0, sticky="w")

    def ver_selec_tipo_graf(self, mostrar):
        if mostrar == 1:
            self.fr_selec_0b.pack()
        else:
            self.fr_selec_0b.pack_forget()

    def selec_frec_graf(self):
        # Frame interior (1b)
        self.fr_selec_1b = tk.Frame(self.fr_selec_1)
        tex_2 = 'Seleccione la frecuencia:'
        self.lab_fr1 = tk.Label(self.fr_selec_1b, text=tex_2)
        self.lab_fr1.grid(row=0, column=0, sticky="w")

        self.var_fr1 = tk.IntVar()
        self.rb0_fr1 = tk.Radiobutton(self.fr_selec_1b,
                                      text='Por día',
                                      variable=self.var_fr1, value=0,
                                      command=self.distribuidor_frame_1)
        self.rb1_fr1 = tk.Radiobutton(self.fr_selec_1b, text='Por mes',
                                      variable=self.var_fr1, value=1,
                                      command=self.distribuidor_frame_1)
        self.rb2_fr1 = tk.Radiobutton(self.fr_selec_1b, text='Por trimestre',
                                      variable=self.var_fr1, value=2,
                                      command=self.distribuidor_frame_1)
        self.rb0_fr1.grid(row=1, column=0, sticky="w")
        self.rb1_fr1.grid(row=2, column=0, sticky="w")
        self.rb2_fr1.grid(row=3, column=0, sticky="w")

    def ver_selec_frec_graf(self, mostrar):
        if mostrar == 1:
            self.fr_selec_1b.pack()
        else:
            self.fr_selec_1b.pack_forget()

    # %% Funciones

    def cargar_certif(self):
        '''Abre un menu para buscar en los archivos la tabla que se desea
        cargar. Carga la tabla en memoria como data frame de pandas'''
        opciones = {
            'title': 'Seleccionar archivo',
            'filetypes': [('Achivos compatibles', '*.xlsx')]
        }
        ruta_tabla = fd.askopenfilename(**opciones)
        self.focus()
        '''
        self.tabla_SJ1 = pd.read_excel(ruta_tabla)
        self.limpiar_base()
        self.la_falta_tabla.forget()
        '''
        crear_db(ruta_tabla)
        self.cartel_area_graf() # Para borrar el cartel si se carga una base de datos

    def create_menu(self):
        # Menu para agregar bases de datos
        self.menu_base = tk.Menu(self)
        self.menu_nuevo = tk.Menu(self.menu_base, tearoff=0)
        self.menu_nuevo.add_command(
            label='Agregar tabla certificados', command=self.cargar_certif)
        self.menu_nuevo.add_command(
            label='Agregar tabla empleados')
        self.menu_base.add_cascade(label='Agregar datos', menu=self.menu_nuevo)
        self.config(menu=self.menu_base)

    def distribuidor_frame_0(self):
        '''Asigna la funcion correcta segun la eleccion en el frame de la
        izquierda'''
        graf = self.var_fr0.get()
        if graf == 0:
            self.opciones_frecuencia(1)
        elif graf == 1:
            self.opciones_frecuencia(1)
        elif graf == 2:
            self.opciones_frecuencia(1)
        elif graf == 3:
            self.opciones_frecuencia(0)

    def distribuidor_frame_1(self):
        '''Verifica que se haya cargado una base de datos y
        asigna la funcion correcta segun la eleccion en el frame de la
        izquierda'''
        hay_base = utils.verif_base_datos('cert')
        if hay_base == 'base_0':
            pass
        else:
            self.mostrar_grafico()

    def limpiar_base(self):
        # Eliminar la columna de fecha de fin de certificado
        self.tabla_SJ2 = self.tabla_SJ1.drop('Validez_Hasta', axis=1)

        # Eliminar filas con NaN en nro legajo o en fecha
        self.tabla_SJ = self.tabla_SJ2.dropna(
            subset=[self.tabla_SJ2.columns[3], self.tabla_SJ2.columns[9]])

        # Eliminar filas con dias negativos
        self.tabla_SJ = self.tabla_SJ[self.tabla_SJ["Dias"] > 0]

    def mostrar_grafico(self):
        frec = self.var_fr1.get()
        if self.var_fr0.get() == 0:
            figura = graficos.aus_simple_tiempo(frec)

        # Limpiar el frame y mostrar el gráfico
        for widget in self.fr_graficos.winfo_children():
            widget.destroy()
   
        # Convertir figura a un Canvas de Tkinter y empaquetarlo en el frame
        canvas = FigureCanvasTkAgg(figura, master=self.fr_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def opciones_frecuencia(self, mostrar):
        '''En caso que haya opciones de como graficar agrupando los datos
        por frecuencia, mostrar el frame de opciones de frecuencias'''

        if mostrar == 1:
            self.ver_selec_frec_graf(1)
        else:
            self.ver_selec_frec_graf(0)

    def set_icon(self):
        # Cargar el icono de la parte superior izquierda 
        self.icon_image = tk.PhotoImage(file=logo)
        self.iconphoto(False, self.icon_image)


# %% Funciones de labels

    def cartel_area_graf(self):
        base_cert = utils.verif_base_datos('cert')

        if base_cert == 'base_0':
            self.la_falta_excel.pack()
        else:
            self.la_falta_excel.destroy()


# %% Iniciar el bucle principal de la interfaz gráfica

    def run(self):
        self.mainloop() 

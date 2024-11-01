# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:52:27 2024

@author: Pablo

Front end para la visualizacion de graficos realizado para el area de RRHH
de la Clinica San Jorge (Ushuaia)
"""
# %% Importaciones
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
            selfset_icon()
        except:
            pass

        # Crear el menu para agregar bases de datos
        self.create_menu()

        # Marco para los graficos
        self.fr_graficos = tk.Frame(self, bg=color_fondo, height=400)
        self.fr_graficos.pack(side="top", fill="x")
        self.la_falta_tabla = tk.Label(
            self.fr_graficos, text='Por favor cargue la tabla con' +
            ' los certificados')

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

        # Frame 0 (izquierda)
        tex_1 = 'Seleccione el gráfico que desea:'
        self.lab_fr0 = tk.Label(self.fr_selec_0, text=tex_1)
        self.lab_fr0.grid(row=0, column=0, sticky="w")

        self.var_fr0 = tk.IntVar()
        self.rb0_fr0 = tk.Radiobutton(self.fr_selec_0,
                                      text='Ausencias totales',
                                      variable=self.var_fr0, value=1,
                                      command=self.distribuidor_frame_0)
        self.rb1_fr0 = tk.Radiobutton(self.fr_selec_0,
                                      text='Ausencias controlables' +
                                      ' vs no controlables',
                                      variable=self.var_fr0, value=2,
                                      command=self.distribuidor_frame_0)
        self.rb2_fr0 = tk.Radiobutton(self.fr_selec_0, text='Ausencias' +
                                      ' justificadas vs injustificadas',
                                      variable=self.var_fr0, value=3,
                                      command=self.distribuidor_frame_0)
        self.rb3_fr0 = tk.Radiobutton(self.fr_selec_0, text='Duración del' +
                                      ' ausentismo',
                                      variable=self.var_fr0, value=4,
                                      command=self.distribuidor_frame_0)
        self.rb0_fr0.grid(row=1, column=0, sticky="w")
        self.rb1_fr0.grid(row=2, column=0, sticky="w")
        self.rb2_fr0.grid(row=3, column=0, sticky="w")
        self.rb3_fr0.grid(row=4, column=0, sticky="w")

        # Frame 1 (izquierda centro)
        # Frame interior (1b)
        self.fr_selec_1b = tk.Frame(self.fr_selec_1)
        tex_2 = 'Seleccione la frecuencia:'
        self.lab_fr1 = tk.Label(self.fr_selec_1b, text=tex_2)
        self.lab_fr1.grid(row=0, column=0, sticky="w")

        self.var_fr1 = tk.IntVar()
        self.rb0_fr1 = tk.Radiobutton(self.fr_selec_1b,
                                      text='Por día',
                                      variable=self.var_fr1, value=1,
                                      command=self.distribuidor_frame_1)
        self.rb1_fr1 = tk.Radiobutton(self.fr_selec_1b,
                                      text='Por mes',
                                      variable=self.var_fr1, value=2,
                                      command=self.distribuidor_frame_1)
        self.rb2_fr1 = tk.Radiobutton(self.fr_selec_1b, text='Por estación',
                                      variable=self.var_fr1, value=3,
                                      command=self.distribuidor_frame_1)
        self.rb3_fr1 = tk.Radiobutton(self.fr_selec_1b, text='Por año',
                                      variable=self.var_fr1, value=4,
                                      command=self.distribuidor_frame_1)
        self.rb0_fr1.grid(row=1, column=0, sticky="w")
        self.rb1_fr1.grid(row=2, column=0, sticky="w")
        self.rb2_fr1.grid(row=3, column=0, sticky="w")
        self.rb3_fr1.grid(row=4, column=0, sticky="w")

    # Funciones

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
        crear_db(self, ruta_tabla)

    def crear_graf_total(self, frec=0):
        lista_fechas = []
        # Iterar sobre las filas del DataFrame
        for _, row in self.tabla_SJ.iterrows():
            # Generar un rango de fechas
            fechas_evento = pd.date_range(
                start=row['Validez_Desde'], periods=row['Dias']).tolist()
            # Añadir la lista de fechas a la lista principal
            lista_fechas.append(fechas_evento)
        return lista_fechas

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
        '''Asigna la fucnion correcta segun la eleccion en el frame de la
        izquierda'''
        if self.var_fr0.get() == 1:
            self.opciones_frecuencia(1)
        elif self.var_fr0.get() == 2:
            self.opciones_frecuencia(1)
        elif self.var_fr0.get() == 3:
            self.opciones_frecuencia(1)
        elif self.var_fr0.get() == 4:
            self.opciones_frecuencia(0)

    def distribuidor_frame_1(self):
        '''Asigna la fucnion correcta segun la eleccion en el frame de la
        izquierda'''
        if not hasattr(self, 'tabla_SJ') or self.tabla_SJ.empty:
            self.la_falta_tabla.forget()
            self.la_falta_tabla.pack()
        else:
            self.la_falta_tabla.forget()
            self.graf_1 = self.mostrar_grafico(self.var_fr1.get())

    def limpiar_base(self):
        # Eliminar la columna de fecha de fin de certificado
        self.tabla_SJ2 = self.tabla_SJ1.drop('Validez_Hasta', axis=1)

        # Eliminar filas con NaN en nro legajo o en fecha
        self.tabla_SJ = self.tabla_SJ2.dropna(
            subset=[self.tabla_SJ2.columns[3], self.tabla_SJ2.columns[9]])

        # Eliminar filas con dias negativos
        self.tabla_SJ = self.tabla_SJ[self.tabla_SJ["Dias"] > 0]

    def mostrar_grafico(self, frec):
        lista_fechas = self.crear_graf_total()
        # Aplanar la lista de listas y contar las apariciones de cada fecha
        fechas_planas = [fecha for sublista in
                         lista_fechas for fecha in sublista]
        conteo_fechas = Counter(fechas_planas)

        # Crear DataFrame para ordenar y graficar
        df_conteo_fechas = pd.DataFrame(conteo_fechas.items(),
                                        columns=['Fecha', 'Frecuencia'])
        df_conteo_fechas = df_conteo_fechas.sort_values('Fecha')

        # Crear figura de Matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_conteo_fechas['Fecha'], df_conteo_fechas['Frecuencia'],
                marker='o', linestyle='-', color='skyblue')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de ausencias')
        ax.set_title('Ausencias por fecha')
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        # Personalizar las etiquetas del eje x
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Limpiar el frame y mostrar el gráfico
        for widget in self.fr_graficos.winfo_children():
            widget.destroy()
   
        # Convertir figura a un Canvas de Tkinter y empaquetarlo en el frame
        canvas = FigureCanvasTkAgg(fig, master=self.fr_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def opciones_frecuencia(self, mostrar):
        if mostrar == 1:
            self.fr_selec_1b.pack()
        else:
            self.fr_selec_1b.forget()

    def set_icon(self):
        # Cargar el icono de la parte superior izquierda 
        self.icon_image = tk.PhotoImage(file=logo)
        self.iconphoto(False, self.icon_image)

    def run(self):
        self.mainloop() # Inicia el bucle principal de la interfaz gráfica

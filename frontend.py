# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:52:27 2024

@author: Pablo

Front end para la visualizacion de graficos realizado para el area de RRHH
de la Clinica San Jorge (Ushuaia)
"""
# %% Importaciones
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import graficos
import utils
from database_setup import crear_db_cert, crear_db_empleados

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
        self.selec_vista_graf()

    # %% Menus de radio buttom

    def selec_tipo_graf(self):
        # Frame 0 (izquierda)
        self.fr_selec_0b = tk.Frame(self.fr_selec_0)
        tex_1 = 'Seleccione el gráfico que desea:'
        self.lab_fr0 = tk.Label(self.fr_selec_0b, text=tex_1,
                                bg='azure4',
                                font=('Helvetica', 11))
        self.lab_fr0.grid(row=0, column=0, sticky="ew")

        # Radio button para seleccionar tipo de grafico
        style = ttk.Style(self)
        style.configure('Custom.TRadiobutton',
                        font=('Arial', 10))
        self.var_fr0 = tk.IntVar(value=-1)
        self.rb0_fr0 = ttk.Radiobutton(self.fr_selec_0b,
                                       text='Ausencias totales',
                                       variable=self.var_fr0, value=0,
                                       command=self.ver_selec_frec_graf,
                                       style='Custom.TRadiobutton')
        self.rb1_fr0 = ttk.Radiobutton(self.fr_selec_0b,
                                       text='Ausencias controlables' +
                                       ' vs no controlables',
                                       variable=self.var_fr0, value=1,
                                       command=self.ver_selec_frec_graf,
                                       style='Custom.TRadiobutton')
        self.rb2_fr0 = ttk.Radiobutton(self.fr_selec_0b, text='Ausencias' +
                                       ' justificadas vs injustificadas',
                                       variable=self.var_fr0, value=2,
                                       command=self.ver_selec_frec_graf,
                                       style='Custom.TRadiobutton')
        self.rb0_fr0.grid(row=1, column=0, sticky="w")
        self.rb1_fr0.grid(row=2, column=0, sticky="w")
        self.rb2_fr0.grid(row=3, column=0, sticky="w")

    def ver_selec_tipo_graf(self, mostrar):
        if mostrar == 1:
            self.fr_selec_0b.pack()
        else:
            self.fr_selec_0b.pack_forget()

    def selec_frec_graf(self):
        # Frame interior (1b)
        self.fr_selec_1b = tk.Frame(self.fr_selec_1)
        tex_2 = 'Seleccione la frecuencia:'
        self.lab_fr1 = tk.Label(self.fr_selec_1b, text=tex_2,
                                bg='azure4',
                                font=('Arial', 10, 'bold'))
        self.lab_fr1.grid(row=0, column=0, sticky="w")

        # Radio button para seleccionar frecuencia
        # Inicializo con un valor que no representa nada ("-1")
        self.var_fr1 = tk.IntVar(value=-1)
        self.rb0_fr1 = ttk.Radiobutton(self.fr_selec_1b,
                                       text='Por día',
                                       variable=self.var_fr1, value=0,
                                       command=self.distribuidor_frame_1)
        self.rb1_fr1 = ttk.Radiobutton(self.fr_selec_1b,
                                       text='Por mes (suma)',
                                       variable=self.var_fr1, value=1,
                                       command=self.distribuidor_frame_1)
        self.rb2_fr1 = ttk.Radiobutton(self.fr_selec_1b,
                                       text='Por mes (promedio)',
                                       variable=self.var_fr1, value=2,
                                       command=self.distribuidor_frame_1)
        self.rb3_fr1 = ttk.Radiobutton(self.fr_selec_1b,
                                       text='Por trimestre (suma)',
                                       variable=self.var_fr1, value=3,
                                       command=self.distribuidor_frame_1)
        self.rb4_fr1 = ttk.Radiobutton(self.fr_selec_1b,
                                       text='Por trimestre (promedio)',
                                       variable=self.var_fr1, value=4,
                                       command=self.distribuidor_frame_1)
        self.rb0_fr1.grid(row=1, column=0, sticky="w")
        self.rb1_fr1.grid(row=2, column=0, sticky="w")
        self.rb2_fr1.grid(row=3, column=0, sticky="w")
        self.rb3_fr1.grid(row=4, column=0, sticky="w")
        self.rb4_fr1.grid(row=5, column=0, sticky="w")

    def selec_vista_graf(self):
        # Radio button para seleccionar total o porcentaje
        self.fr_selec_2b = tk.Frame(self.fr_selec_2)
        tex_2b = 'Ver las ausencias:'
        self.lab_fr1 = tk.Label(self.fr_selec_2b, text=tex_2b,
                                bg='azure4',
                                font=('Arial', 10, 'bold'))
        self.lab_fr1.grid(row=0, column=0, sticky="w")

        # Inicializo con total
        self.var_fr2 = tk.IntVar(value=0)
        self.rb0_fr2 = ttk.Radiobutton(self.fr_selec_2b,
                                       text='Absolutas',
                                       variable=self.var_fr2, value=0,
                                       command=self.distribuidor_frame_2)
        self.rb1_fr2 = ttk.Radiobutton(self.fr_selec_2b, text='Proporcionales',
                                       variable=self.var_fr2, value=1,
                                       command=self.distribuidor_frame_2)
        self.rb0_fr2.grid(row=1, column=0, sticky="w")
        self.rb1_fr2.grid(row=2, column=0, sticky="w")

    def ver_selec_frec_graf(self):
        self.fr_selec_1b.pack()
        mostrar = self.var_fr0.get()
        if mostrar in [1, 2]:
            self.fr_selec_2b.pack_forget()
            self.var_fr2.set(0)

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
        crear_db_cert(ruta_tabla)
        self.cartel_area_graf() # Para borrar el cartel si se carga una base de datos


    def cargar_empleados(self):
        '''Abre un menu para buscar en los archivos la tabla de
        los empleados de la clinica'''
        opciones = {
            'title': 'Seleccionar archivo',
            'filetypes': [('Achivos compatibles', '*.xlsx')]
        }
        ruta_tabla = fd.askopenfilename(**opciones)
        self.focus()
        crear_db_empleados(ruta_tabla)

    def create_menu(self):
        '''Menu para agregar bases de datos y ver creditos'''
        self.menu_base = tk.Menu(self)
        # Agregar tablas de certificados
        self.menu_agregar = tk.Menu(self.menu_base, tearoff=0)
        self.menu_agregar.add_command(
            label='Agregar tabla certificados', command=self.cargar_certif)
        self.menu_agregar.add_command(
            label='Agregar tabla empleados', command=self.cargar_empleados)
        self.menu_base.add_cascade(label='Agregar datos', menu=self.menu_agregar)
        self.config(menu=self.menu_base)

        # Ver creditos del programa
        self.menu_creditos = tk.Menu(self.menu_base, tearoff=0)
        self.menu_creditos.add_command(
            label='Créditos', command=self.ver_creditos)
        self.menu_base.add_cascade(label='Creditos', menu=self.menu_creditos)
        self.config(menu=self.menu_base)

    def distribuidor_frame_1(self):
        # Frame de frecuencias
        '''Verifica que se haya cargado una base de datos y
        asigna la funcion correcta segun la eleccion en el frame de la
        izquierda'''
        hay_base = utils.verif_base_datos('cert')
        if hay_base == 'base_0':
            # En caso que no se haya cargado la tabla de certificados
            pass
        elif self.var_fr0.get() == 0:
            # Ausencias totales
            self.mostrar_grafico(0)
        elif self.var_fr0.get() == 1:
            # Controlables vs no controlables
            self.fr_selec_2b.pack_forget()
            self.var_fr2.set(0)
            self.mostrar_grafico(1)
        elif self.var_fr0.get() == 2:
            # Justificadas vs no justificadas
            self.fr_selec_2b.pack_forget()
            self.var_fr2.set(0)
            self.mostrar_grafico(2)
        
        # Solo ver ausencias proporcionales con frecuencia
        # diaria o promedio
        if self.var_fr0.get() == 0:
            if self.var_fr1.get() in [0, 2, 4]:
                self.fr_selec_2b.pack()
            elif self.var_fr1.get() in [1, 3]:
                self.fr_selec_2b.pack_forget()
                self.var_fr2.set(0)

    def distribuidor_frame_2(self):
        '''Verifica que se haya cargado la base
        de datos de empleados para los graficos
        de propocion. Asigna la funcion segun el 
        radio button de vista'''
        hay_base = utils.verif_base_datos('empleados')
        if hay_base == 'base_0':
            pass  # Evita el error si no hay base de empleados
        elif self.var_fr0.get() == 0:  # Si el grafico es de ausencias totales
            # Faltas absolutas o porcentuales
            vista = self.var_fr2.get()
            if vista == 0:
                self.mostrar_grafico(0)
            elif vista == 1:
                self.mostrar_grafico(0, 1)
            
    def mostrar_grafico(self, tipo, vista=0):
        frec = self.var_fr1.get()  # Frecuencia: dia, mes o trimestre
        if vista == 0:
            figura = graficos.aus_simple_tiempo(frec, tipo)
        
        elif vista == 1:
            figura = graficos.aus_simple_tiempo(frec, tipo, vista)

        # Limpiar el frame y mostrar el gráfico
        for widget in self.fr_graficos.winfo_children():
            widget.destroy()
        plt.close('all')
   
        # Convertir figura a un Canvas de Tkinter y empaquetarlo en el frame
        canvas = FigureCanvasTkAgg(figura, master=self.fr_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def set_icon(self):
        # Cargar el icono de la parte superior izquierda 
        self.icon_image = tk.PhotoImage(file=logo)
        self.iconphoto(False, self.icon_image)

    def ver_creditos(self):
        '''Abrir una nueva ventana con
        creditos de autores de este programa'''
        self.creditos = tk.Toplevel(self)
        self.creditos.title('Créditos')
        self.creditos.geometry('500x145')
        self.creditos.resizable(False, False)
        self.creditos.iconphoto(False, self.icon_image)

        self.frame_creditos = tk.Frame(self.creditos, bg='azure4')
        self.frame_creditos.pack(expand=True, fill='both')

        creditos = '''Autores:   Pablo Jusim (pablo.jusim@gmail.com)
                    Stella Ventura
                    Luciano Luna
                    Ana Ramos
                    Marcelo Renzone'''
        lb_creditos = tk.Label(self.frame_creditos, text=creditos,
                               justify='left', font=("Arial", 16),
                               bg='azure4')
        lb_creditos.pack(pady=10)


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

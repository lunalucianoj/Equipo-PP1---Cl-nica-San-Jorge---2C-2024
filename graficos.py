'''Este modulo contiene las funciones para llamar a la base de datos y crear los graficos
solicitados en el frontend'''

from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from database_setup import abrir_bd, cerrar_bd

# %% Funciones para organizar

def aus_simple_tiempo(frec, tipo):
    # Consulta SQL, fechas y duración por certificado
    datos_1 = sql_aus_simple_tiempo()
    fechas_org = organizar_fechas(datos_1, frec)
    if tipo == 0:
        figura = graficar_0(fechas_org, frec)
    if tipo == 2:
        figura = graficar_2(fechas_org, frec)
    return figura


def organizar_fechas(datos, frec):
    df_fechas = pd.DataFrame(datos, columns=[
        'Fecha', 'justificado', 'no_justificado', 'no_controlable'])
    # Asegurarse de que sean datetime
    df_fechas['Fecha'] = pd.to_datetime(df_fechas['Fecha'])

    df_fechas_2 = None
    if frec == 0:  # Dia
        df_fechas_2 = df_fechas
    elif frec == 1:  # Mes
        df_fechas.set_index('Fecha', inplace=True)
        df_fechas_2 = df_fechas.resample('ME').sum().reset_index()
    elif frec == 2:  # Trimestre
        df_fechas.set_index('Fecha', inplace=True)
        df_fechas_2 = df_fechas.resample('QE').sum().reset_index()
    
    return df_fechas_2

# %%  Funciones para graficar


def graficar_0(fechas, frec):
    '''Crea los graficos de ausencias totales 
    que se van a usar en el frontend.'''


    fechas.fillna(0, inplace=True)
    # Agregar una nueva columna 'total_ausencias' que sea la suma de las
    # columnas
    fechas['total_ausencias'] = fechas['justificado'] + fechas['no_justificado'] +\
    fechas['no_controlable']

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['total_ausencias'], marker='o', linestyle='-')
    ax.set_ylabel('Frecuencia de Ausencias')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.3, left=0.1, right=0.9)

    if frec == 0:  # Dia
        ax.set_title('Frecuencia de Ausencias por día')
        ax.set_xlabel('Fecha')
        ax.plot(fechas['Fecha'], fechas['total_ausencias'], marker=None, linestyle='-')
    elif frec == 1:  # Mes
        ax.set_title('Frecuencia de Ausencias por Mes')
        ax.set_xlabel('Mes')
    elif frec == 2:  # Trimestre
        ax.set_title('Frecuencia de Ausencias por Trimestre')
        # Configurar etiquetas del eje X
        trimestres = fechas['Fecha']
        ax.set_xticks(trimestres)  # Establecer posiciones de los ticks
        # Crear etiquetas con el formato "trimestre 1 2023"
        labels = [f'Trimestre {date.quarter} {
            date.year}' for date in trimestres]
        ax.set_xticklabels(labels, rotation=35)
        ax.xaxis.set_tick_params(pad=10)
    return fig

def graficar_2(fechas, frec):
    '''Crea los graficos de ausencias justificadas vs no justificadas 
    que se van a usar en el frontend.'''


    fechas.fillna(0, inplace=True)

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['justificado'], label='Ausencias justificadas',
            marker='o', linestyle='-')
    ax.plot(fechas['Fecha'], fechas['no_justificado'], label='Ausencias no justificadas',
            marker='o', linestyle='-')

    ax.set_ylabel('Frecuencia de Ausencias')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.3, left=0.1, right=0.9)

    if frec == 0:  # Dia
        ax.set_title('Frecuencia de Ausencias por día')
        ax.set_xlabel('Fecha')
    elif frec == 1:  # Mes
        ax.set_title('Frecuencia de Ausencias por Mes')
        ax.set_xlabel('Mes')
    elif frec == 2:  # Trimestre
        ax.set_title('Frecuencia de Ausencias por Trimestre')
        # Configurar etiquetas del eje X
        trimestres = fechas['Fecha']
        ax.set_xticks(trimestres)  # Establecer posiciones de los ticks
        # Crear etiquetas con el formato "trimestre 1 2023"
        labels = [f'Trimestre {date.quarter} {
            date.year}' for date in trimestres]
        ax.set_xticklabels(labels, rotation=35)
        ax.xaxis.set_tick_params(pad=10)

    # Mostrar la leyenda
    ax.legend()
    return fig


# %% Consultas SQL


def sql_aus_simple_tiempo():
    sql = '''SELECT *
             FROM ausencias
             ORDER BY fecha'''
    return sql_varias_filas(sql)


def sql_varias_filas(consulta):
    '''Ejecuta la consulta sql que se indique
    Input: consulta sql escrita correctamente
    Output: Lo que devuelva la base de datos'''
    conn, cur = abrir_bd()
    cur.execute(consulta)
    inicio_certificados = cur.fetchall()
    cerrar_bd()
    return inicio_certificados


# %% Funciones auxiliares para los graficos

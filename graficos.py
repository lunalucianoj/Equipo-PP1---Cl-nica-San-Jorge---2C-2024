'''Este modulo contiene las funciones para llamar a la base de datos y crear los graficos
solicitados en el frontend'''

from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from database_setup import abrir_bd, cerrar_bd

# %% Funciones para organizar

def aus_simple_tiempo(frec, tipo, vista = 0):
    # Consulta SQL, fechas y duración por certificado
    datos_1 = sql_aus_simple_tiempo()
    fechas_org = organizar_fechas(datos_1, frec)
    figura = None
    if vista == 0:
        figura = graficar_tiempo(fechas_org, frec, tipo)
    elif vista == 1:
        figura = graficar_tiempo(fechas_org, frec, tipo, vista)
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


def graficar_tiempo(fechas, frec, tipo, vista = 0):
    '''Creo los gráficos de ausencias en función del tiempo'''

    # Preparar los datos segun el tipo de grafico
    fig, ax = plt.subplots()
    if tipo == 0 and vista == 0:
        # Totales
        fig, ax = preparar_graf_0(fechas)
    elif tipo == 0 and vista == 1:
        # Totales proporcion de ausencias
        fig, ax = preparar_graf_0_porc(fechas)
    elif tipo == 1:
        # Controlable vs no controlable
        fig, ax = preparar_graf_1(fechas)
    elif tipo == 2:
        # Justificada vs no justificada
        fig, ax = preparar_graf_2(fechas)

    ax.set_ylabel('Frecuencia de Ausencias')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.3, left=0.1, right=0.9)
    primer_dia_mes = fechas[fechas['Fecha'].dt.is_month_start]['Fecha']

    if frec == 0:  # Dia
        ax.set_title('Frecuencia de Ausencias por día')
        ax.set_xlabel('Fecha')
        ax.set_xticks(primer_dia_mes)
        ax.set_xticklabels(primer_dia_mes.dt.strftime('%Y-%m-%d'),
                           rotation=45, ha='right')
        for x in primer_dia_mes:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
    elif frec == 1:  # Mes
        ax.set_title('Frecuencia de Ausencias por Mes')
        ax.set_xlabel('Mes')
        ax.set_xticks(fechas['Fecha'])
        ax.set_xticklabels(fechas['Fecha'].dt.strftime('%Y-%m'),
                           rotation=45, ha='right')
        for x in fechas['Fecha']:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
    elif frec == 2:  # Trimestre
        ax.set_title('Frecuencia de Ausencias por Trimestre')
        # Configurar etiquetas del eje X
        trimestres = fechas['Fecha']
        ax.set_xticks(trimestres)  # Establecer posiciones de los ticks
        # Crear etiquetas con el formato "trimestre 1 2023"
        labels = [f'Trimestre {date.quarter} {
            date.year}' for date in trimestres]
        ax.set_xticklabels(labels, ha='right')
        ax.set_xticklabels(labels, rotation=35)
        ax.xaxis.set_tick_params(pad=10)
        for x in trimestres:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
    
    return fig


def preparar_graf_0(fechas):
    '''Crea los graficos de ausencias totales 
    que se van a usar en el frontend.'''

    fechas.fillna(0, inplace=True)
    # Agregar una nueva columna 'total_ausencias' que sea la suma de las
    # columnas
    fechas['total_ausencias'] = fechas['justificado'] +\
        fechas['no_justificado'] + fechas['no_controlable']

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['total_ausencias'],
            linestyle='-')
 
    return fig, ax


def preparar_graf_0_porc(fechas):
    '''Crea los graficos de ausencias totales 
    que se van a usar en el frontend.
    Usa porcentaje de ausencias'''

    fechas.fillna(0, inplace=True)
    # Agregar una nueva columna 'total_ausencias' que sea la suma de las
    # columnas
    fechas['total_ausencias'] = fechas['justificado'] +\
        fechas['no_justificado'] + fechas['no_controlable']
    
    # Contar la cantidad de empleados
    conn, cur = abrir_bd()
    cur.execute('SELECT COUNT(nro_legajo) FROM empleados')
    nro_empleados = cur.fetchone()[0]
    cerrar_bd()
    fechas['total_ausencias_porc'] = (fechas['total_ausencias'] /
                                      nro_empleados) * 100
    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['total_ausencias_porc'],
            linestyle='-')
 
    return fig, ax


def preparar_graf_1(fechas):
    '''Crea los graficos de ausencias controlables vs no controlables
    que se van a usar en el frontend.'''

    fechas.fillna(0, inplace=True)
    # Agregar una nueva columna 'controlables' que sea la suma
    # de las justificadas y las no justificadas
    fechas['controlables'] = fechas['justificado'] + fechas['no_justificado']

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['controlables'],
            label='Ausencias controlables',
            marker=None, linestyle='-')
    ax.plot(fechas['Fecha'], fechas['no_controlable'],
            label='Ausencias no controlables',
            marker=None, linestyle='-')
    # Mostrar la leyenda
    ax.legend()

    return fig, ax


def preparar_graf_2(fechas):
    '''Crea los graficos de ausencias justificadas vs no justificadas 
    que se van a usar en el frontend.'''

    fechas.fillna(0, inplace=True)

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['justificado'],
            label='Ausencias justificadas',
            marker=None, linestyle='-')
    ax.plot(fechas['Fecha'], fechas['no_justificado'],
            label='Ausencias no justificadas',
            marker=None, linestyle='-')
    # Mostrar la leyenda
    ax.legend()

    return fig, ax


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

'''Este modulo contiene las funciones para llamar a la base de datos y crear los graficos
solicitados en el frontend'''

import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
from database_setup import abrir_bd, cerrar_bd


# %% Funciones para organizar

def aus_simple_tiempo(frec):
    # Consulta SQL, fechas y duración por certificado
    datos_1 = sql_aus_simple_tiempo()
    datos_2 = crear_dic_fechas(datos_1)  # Crear diccionario de fechas
    fechas_org = organizar_fechas(datos_2, frec)
    figura = graficar_1(fechas_org, frec)
    return figura


def organizar_fechas(datos, frec):
    df_fechas = pd.DataFrame(list(datos.items()), columns=[
        'Fecha', 'Frecuencia'])
    # Asegurarse de que sean datetime
    df_fechas['Fecha'] = pd.to_datetime(df_fechas['Fecha'])

    if frec == 0:  # Dia
        df_fechas_2 = df_fechas.sort_values('Fecha')  # Ordenar por fecha
    elif frec == 1:  # Mes
        df_fechas.set_index('Fecha', inplace=True)
        df_fechas_2 = df_fechas.resample('ME').sum().reset_index()
    elif frec == 2:  # Trimestre
        df_fechas.set_index('Fecha', inplace=True)
        df_fechas_2 = df_fechas.resample('QE').sum().reset_index()
    
    return df_fechas_2

# %%  Funciones para graficar


def graficar_1(fechas, frec):

    # Crear la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(fechas['Fecha'], fechas['Frecuencia'], marker='o', linestyle='-')
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
        labels = [f'Trimestre {date.quarter} {date.year}' for date in trimestres]
        ax.set_xticklabels(labels, rotation=35)
        ax.xaxis.set_tick_params(pad=10)
    return fig


# %% Consultas SQL


def sql_aus_simple_tiempo ():
    sql = '''SELECT c.validez_dde, c.validez_hta
             FROM certificados AS c
             JOIN tcd AS t
             WHERE t.id_agr = 0 OR t.id_agr = 3'''
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

def crear_dic_fechas(tabla_SJ):
    '''Input: Fechas de inicio y fin de los certificados
    Output: diccionario de fechas:
    clave: fecha
    valor: cantidad de ausencias en esa fecha.
    '''
    # Crear un contador para acumular las frecuencias
    contador_fechas = Counter()

    # Iterar sobre cada tupla de (fecha_inicio, fecha_fin)
    for inicio, fin in tabla_SJ:
        # Crear el rango de fechas y actualizar el contador
        rango_fechas = pd.date_range(start=inicio, end=fin)
        contador_fechas.update(rango_fechas)
    return contador_fechas

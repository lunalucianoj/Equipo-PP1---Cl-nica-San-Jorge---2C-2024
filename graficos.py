'''Este modulo contiene las funciones para llamar a la base de datos y crear los graficos
solicitados en el frontend'''

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from collections import defaultdict
from database_setup import abrir_bd, cerrar_bd


# %% Funciones para graficar

def aus_simple_tiempo():
    datos_1 = sql_aus_simple_tiempo()  # Consulta SQL, fechas y duración por certificado
    datos_2 = crear_dic_fechas(datos_1)  # Crear diccionario de fechas
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(list(datos_2.keys()), list(datos_2.values()),
            marker='o', color='skyblue')

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad de ausencias')
    ax.set_title('Ausencias por fecha')

    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Personalizar las etiquetas del eje x
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

# %% Consultas SQL


def sql_aus_simple_tiempo ():
    sql = '''SELECT c.validez_dde, c.dias
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
    '''Input: Fechas de inicio y duracion de los certificados
    Output: diccionario de fechas:
    clave: fecha
    valor: cantidad de ausencias en esa fecha.
    '''
    # Usa defaultdict para evitar comprobaciones de existencia
    dic_fechas = defaultdict(int)
    todas_fechas = []  # Crear una lista de todas las fechas con ausencias
    # Iterar sobre las filas del DataFrame
    print('punto_1')
    for inicio, duracion in tabla_SJ:
        fechas_evento = pd.date_range(start=inicio, periods=duracion).to_list()
        # Agregar el rango de fechas a la lista
        todas_fechas.extend(fechas_evento)
    print('punto_2')

    # Convertir la lista a una Serie de pandas y contar cada fecha
    fechas_serie = pd.Series(todas_fechas)
    conteo_fechas = fechas_serie.value_counts()

    # Convertir a diccionario
    dic_fechas = conteo_fechas.to_dict()
    '''
    for row in tabla_SJ:
        # Generar un rango de fechas
        fechas_evento = pd.date_range(
            start=row[0], periods=row[1]).tolist()
        # Sumar los dias con ausencias al diccionario
        for dia in fechas_evento:
            if dia in dic_fechas:
                dic_fechas[dia] += 1
            else:
                dic_fechas[dia] = 1
                '''
    return dic_fechas

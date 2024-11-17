'''Este modulo contiene las funciones para llamar a la base de datos y crear
los graficos solicitados en el frontend'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from datetime import datetime
import pandas as pd
from database_setup import abrir_bd, cerrar_bd

# %% Funcion principal de orden


def ordenar_datos_grafico(tipo, separ, frec, agrup, vista, f_min, f_max,
                          medidas):
    '''Esta funcion centraliza la creacion de cualquier grafico
    Llama a las funciones correspondientes segun el grafico
    Output: Grafico creado para pasar a frontend'''
    if tipo == 0:  # Gráficos por tiempo
        # Levantar data entre fechas inidicadas
        fechas_data = levantar_fechas(f_min, f_max)
        fechas_tipo = fechas_por_tipo(fechas_data, separ)
        fechas_frec_agrup = fechas_por_agrup(fechas_tipo, frec, agrup)
        fechas_vista = fechas_por_vista(fechas_frec_agrup, vista)
    elif tipo == 1:  # Gráficos por departamento
        fechas_dpto = levantar_fechas_dpto(f_min, f_max)
    # Hacer los graficos
    figura = ordenar_grafico(fechas_vista, separ, agrup, vista, medidas, frec)

    return figura


def ordenar_grafico(fechas, separ, agrup, vista, medidas, frec):
    '''Centraliza los llamados a las funciones que
    hacen cada paso de los graficos'''
    figura_base = preparar_base(medidas)
    fig_con_data = agregar_datos(figura_base, fechas, separ)
    fig_eje_x = poner_eje_x(fig_con_data, fechas, frec)
    fig_eje_y = poner_eje_y(fig_eje_x, agrup, vista)
    return fig_eje_y[0]

# %% Organizar datos para graficar


def levantar_fechas(f_min, f_max):
    '''Consulta SQL para obtener las fechas de ausencia
    según los límites de fechas indicados'''
    sql = '''SELECT *
            FROM ausencias
            WHERE fecha BETWEEN ? AND ?
            ORDER BY fecha'''
    _, cur = abrir_bd()
    cur.execute(sql, (f_min, f_max))
    fechas = cur.fetchall()
    cerrar_bd()
    # Convertir fechas_data a pandas data frame
    fechas_data = pd.DataFrame(fechas, columns=[
        'Fecha', 'justificado', 'no_justificado', 'no_controlable'])
    # Asegurarse de que sean datetime
    fechas_data['Fecha'] = pd.to_datetime(fechas_data['Fecha'])
    return fechas_data


def fechas_por_tipo(fechas_data, tipo):
    '''Ordenar las ausencias por tipo de gráfico'''
    if tipo == 0:  # Ausencias totales
        fechas_data['total_ausencias'] = fechas_data['justificado'] +\
            fechas_data['no_justificado'] + fechas_data['no_controlable']
    elif tipo == 1:  # Ausencias controlables vs no
        fechas_data['controlables'] = fechas_data['justificado'] +\
            fechas_data['no_justificado']
    elif tipo == 2:  # Ausencias justificadas vs no
        pass
    return fechas_data


def fechas_por_agrup(fechas, frec, agrup):
    '''Agrupar las ausencias según la frecuecia determinada.
       El agrupamiento es mediante suma o promedio'''
    fechas_agrupadas = None  # Inicializo la variable
    if frec == 0:  # Agrupar por día
        fechas_agrupadas = fechas
    elif frec == 1 and agrup == 0:  # Agrupar suma por mes
        fechas.set_index('Fecha', inplace=True)
        fechas_agrupadas = fechas.resample('ME').sum().reset_index()
    elif frec == 1 and agrup == 1:  # Agrupar promedio por mes
        fechas.set_index('Fecha', inplace=True)
        fechas_agrupadas = fechas.resample('ME').mean().reset_index()
    elif frec == 2 and agrup == 0:  # Agrupar suma por trimestre
        fechas.set_index('Fecha', inplace=True)
        fechas_agrupadas = fechas.resample('QE').sum().reset_index()
    elif frec == 2 and agrup == 1:  # Agrupar promedio por trimestre
        fechas.set_index('Fecha', inplace=True)
        fechas_agrupadas = fechas.resample('QE').mean().reset_index()

    return fechas_agrupadas


def fechas_por_vista(fechas, vista):
    '''Ordena los datos para ver ausencias totales (no hace nada)
    o porcentaje de ausencias (segun empleados totales)'''
    if vista == 0:  # Ausencias totales
        pass  # Para devolver las fechas como estaban
    elif vista == 1:  # Ausencias percentuales
        # Contar la cantidad de empleados
        _, cur = abrir_bd()
        cur.execute('SELECT COUNT(nro_legajo) FROM empleados')
        nro_empleados = cur.fetchone()[0]
        cerrar_bd()
        fechas['total_ausencias'] = (fechas['total_ausencias'] /
                                     nro_empleados) * 100
    return fechas


def levantar_fechas_dpto(f_min, f_max):
    '''Devuelve la cantidad de ausencias por departamento'''
    nro_dptos = listar_dptos()
    df_ausencias = hacer_df_aus(nro_dptos, f_min, f_max)
            


def listar_dptos():
    '''Devuelve la cantidad de departamentos de la clínica'''
    sql = '''SELECT max(id_dep)
          FROM departamentos'''
    _, cur = abrir_bd()
    cur.execute(sql)
    nro_dptos = cur.fetchone()[0]
    cerrar_bd()
    return nro_dptos


def hacer_df_aus(nro_dptos, f_min, f_max):
    '''Devuelve un DataFrame con las fechas de ausencia de cada departamento'''
    ids = []
    ausencias = []
    for id in range(nro_dptos + 1):
        fechas_crudas_dpto = consultar_fechas_dpto(f_min, f_max, id)
        ausencias_dpto = 0
        for cert in fechas_crudas_dpto:
            fecha_0 = datetime.strptime(cert[0], '%Y-%m-%d')
            fecha_1 = datetime.strptime(cert[1], '%Y-%m-%d')
            duracion = (fecha_1 - fecha_0).days + 1
            ausencias_dpto += duracion
        ids.append(id)
        ausencias.append(ausencias_dpto)

    df = pd.DataFrame({
        'id_dpto': ids,
        'ausencias_dpto': ausencias
    })
    return df


def consultar_fechas_dpto(f_min, f_max, dpto):
    '''Consulta la base sql y devuelve la cantidad de ausencias por
    departamento en el período indicado'''
    sql = '''SELECT c.validez_dde, c.validez_hta
             FROM certificados as c
             JOIN empleados as e
             ON c.nro_legajo = e.nro_legajo
             WHERE c.validez_dde >= ?
             AND c.validez_hta <= ?
             AND e.id_dep = ?'''
    _, cur = abrir_bd()
    cur.execute(sql, (f_min, f_max, dpto))
    datos_seq = cur.fetchall()
    cerrar_bd()
    return datos_seq
# %% Hacer graficos


def preparar_base(medidas):
    '''Creo una figura vacia del tamaño buscado'''
    ancho1, alto1 = medidas  # pixeles
    ancho = ancho1 / 100
    alto = alto1 / 100
    fig, ax = plt.subplots(figsize=(ancho, alto))  # en pulgadas
    fig.subplots_adjust(bottom=0.3)
    return fig, ax


def agregar_datos(figura_base, fechas, tipo):
    '''Agrega los datos a la figura base'''
    fig, eje = figura_base
    eje_x = fechas['Fecha']
    if tipo == 0:  # Ausencias totales
        eje.plot(eje_x, fechas['total_ausencias'],
                 label='Ausencias totales',
                 marker=None, linestyle='-')
    elif tipo == 1:  # controlables vs no
        eje.plot(eje_x, fechas['controlables'],
                 label='Ausencias controlables',
                 marker=None, linestyle='-')
        eje.plot(eje_x, fechas['no_controlable'],
                 label='Ausencias no controlables',
                 marker=None, linestyle='-')
    elif tipo == 2:  # justificadas vs no
        eje.plot(eje_x, fechas['justificado'],
                 label='Ausencias justificadas',
                 marker=None, linestyle='-')
        eje.plot(eje_x, fechas['no_justificado'],
                 label='Ausencias no justificadas',
                 marker=None, linestyle='-')

    # Mostrar la leyenda
    eje.legend()
    return fig, eje


def poner_eje_x(figura, fechas, frec):
    '''Establece que se muestra en el eje x segun el
    tipo de grafico. También el título de gráfico'''
    fig, eje = figura
    labels = None
    if frec == 0:
        eje.set_title('Ausencias por Día')  # título grafico
        primer_dia = fechas[fechas['Fecha'].dt.is_month_start]['Fecha']
        eje.set_xlabel('Fecha')
        eje.set_xticks(primer_dia)
        eje.set_xticklabels(primer_dia.dt.strftime('%Y-%m-%d'),
                            rotation=45, ha='right')
        for x in primer_dia:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
    elif frec == 1:
        eje.set_title('Ausencias por Mes')  # título grafico
        eje.set_xlabel('Mes')
        eje.set_xticks(fechas['Fecha'])
        eje.set_xticklabels(fechas['Fecha'].dt.strftime('%Y-%m'),
                            rotation=45, ha='right')
        for x in fechas['Fecha']:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
    elif frec == 2:
        eje.set_title('Ausencias por Trimestre')  # título grafico
        trimestres = fechas['Fecha']
        labels = [f'Trimestre {date.quarter} {
            date.year}' for date in trimestres]
        for x in trimestres:
            plt.axvline(x=x, linestyle='-', linewidth=0.4, color='lightgrey')
        eje.set_xticklabels(labels, ha='right')
        eje.set_xticklabels(labels, rotation=35)
        eje.xaxis.set_tick_params(pad=10)

    return fig, eje


def poner_eje_y(figura, agrup, vista):
    '''Fija el título del eje Y y la forma de
    mostrar los valores'''
    fig, eje = figura
    if vista == 0:  # Ausencias totales
        if agrup == 0:  # Suma de ausencias
            eje.set_ylabel('Ausencias totales')
        elif agrup == 1:  # Promedio de ausencias
            eje.set_ylabel('Ausencias medias')
    elif vista == 1:  # Porcentaje de ausencias
        eje.yaxis.set_major_formatter(mtick.PercentFormatter())
        if agrup == 0:  # Suma de ausencias
            eje.set_ylabel('Porcentaje de ausencias totales')
        elif agrup == 1:  # Promedio de ausencias
            eje.set_ylabel('Porcentaje de ausencias medias')

    return fig, eje

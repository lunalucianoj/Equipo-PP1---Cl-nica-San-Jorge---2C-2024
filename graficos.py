'''Este modulo contiene las funciones para llamar a la base de datos y crear
los graficos solicitados en el frontend'''

from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from database_setup import abrir_bd, cerrar_bd

# %% Funcion principal de orden


def ordenar_datos_grafico(tipo, separ, frec, agrup, vista, f_min, f_max,
                          medidas):
    '''Esta funcion centraliza la creacion de cualquier grafico
    Llama a las funciones correspondientes segun el grafico
    Output: Grafico creado para pasar a frontend'''
    figura = None
    if tipo == 0:  # Gráficos por tiempo
        # Levantar data entre fechas inidicadas
        fechas_data = levantar_fechas(f_min, f_max)
        fechas_tipo = fechas_por_tipo(fechas_data, separ)
        fechas_frec_agrup = fechas_por_agrup(fechas_tipo, frec, agrup)
        fechas_vista = fechas_por_vista(fechas_frec_agrup, vista)
        figura = ordenar_grafico(fechas_vista, separ, agrup, vista,
                                 medidas, frec)
    elif tipo == 1:  # Gráficos por departamento
        ausencias_dpto = levantar_fechas_dpto(f_min, f_max)
        figura = ordenar_grafico_dpto(ausencias_dpto, medidas, separ, vista)
    
    return figura


def ordenar_grafico(fechas, separ, agrup, vista, medidas, frec):
    '''Centraliza los llamados a las funciones que
    hacen cada paso de los graficos'''
    figura_base = preparar_base(medidas)
    fig_con_data = agregar_datos(figura_base, fechas, separ)
    fig_eje_x = poner_eje_x(fig_con_data, fechas, frec)
    fig_eje_y = poner_eje_y(fig_eje_x, agrup, vista)
    return fig_eje_y[0]


def ordenar_grafico_dpto(aus, medidas, separ, vista):
    '''Centraliza las llamadas a funciones para hacer el gráfico
    por departamento'''
    figura_base = preparar_base_dpto(medidas)
    fig_con_data = agregar_datos_dpto(figura_base, aus, separ, vista)
    fig_eje_x = poner_eje_x_dpto(fig_con_data, aus)
    fig_eje_y = poner_eje_y_dpto(fig_eje_x, vista)
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
    '''Devuelve la cantidad de ausencias por departamento
    ordenadas'''
    nro_dptos = contar_dptos()
    df_ausencias = hacer_df_aus(nro_dptos, f_min, f_max)
    aus_con_nobre_dpto = nombrar_dptos(df_ausencias)
    return aus_con_nobre_dpto
            

def contar_dptos():
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
    aus_jus = []
    aus_injus = []
    aus_incon = []
    # Tipos de ausencia ()

    for i in range(nro_dptos + 1):
        # Certificados completamente entre las fechas
        aus_dpto = consultar_fechas_dpto(f_min, f_max, i)
        aus_jus.append(aus_dpto['jus'])
        aus_injus.append(aus_dpto['injus'])
        aus_incon.append(aus_dpto['incon'])
        ids.append(i)

    data = {
        'id_dpto': ids,
        'justificadas': aus_jus,
        'injustificadas': aus_injus,
        'incontrolables': aus_incon
        }
    df = pd.DataFrame(data)
    return df


def consultar_fechas_dpto(f_min, f_max, dpto):
    '''Consulta la base sql y devuelve la cantidad de ausencias por
    departamento en el período indicado separadas por tipo de
    ausencias
    Outpt: diccionario'''
    sql = '''SELECT c.validez_dde AS desde, c.validez_hta AS hasta,
             t.id_agr, t.id_tc
             FROM certificados as c
             JOIN empleados as e ON c.nro_legajo = e.nro_legajo
             JOIN tcd AS t ON c.id_tc = t.id_tc
             WHERE ((c.validez_dde >= ? AND c.validez_dde <= ?)
             OR (c.validez_hta >= ? AND c.validez_hta <= ?)
             OR (c.validez_dde <= ? AND c.validez_hta >= ?))
             AND e.id_dep = ?
             AND (t.id_agr = 0
             OR t.id_agr = 4)'''
    _, cur = abrir_bd()
    cur.execute(sql, (f_min, f_max, f_min, f_max, f_min, f_max, dpto))
    datos_seq = cur.fetchall()
    cerrar_bd()
    datos_corr = corregir_lim(datos_seq, f_min, f_max)
    ausencias_dpto = ausencias_tipo(datos_corr)
    return ausencias_dpto


def corregir_lim(certificados, f_min, f_max):
    '''En los certificados con fechas de inicio previas al
    período reemplaza la fecha de inicio por f_min.
    Lo mismo para fechas de finalización posteriores'''
    certificados_mod = []
    for cert in certificados:
        cert = list(cert)
        # Convertir las fechas a datetime
        inicio = datetime.strptime(cert[0], '%Y-%m-%d').date()
        fin = datetime.strptime(cert[1], '%Y-%m-%d').date()

        if inicio < f_min:
            # Inicio provio al rango
            inicio = f_min
        if fin > f_max:
            # Fin posterior al rango
            fin = f_max

        cert[0] = inicio
        cert[1] = fin
        certificados_mod.append(cert)
    return certificados_mod


def ausencias_tipo(datos):
    '''Devuelve la cantidad de ausencias por tipo de certificado'''
    ausencias = {'jus': 0, 'injus': 0, 'incon': 0}
    for cert in datos:
        dias = contar_ausencias(cert)
        if cert[3] == 29:  # Injustificadas
            ausencias['injus'] += dias
        elif cert[2] == 0 and cert[3] != 29:  # Justificadas
            ausencias['jus'] += dias         
        elif cert[2] == 4:  # Incontrolable
            ausencias['incon'] += dias
    return ausencias


def contar_ausencias(cert):
    '''Cuenta las ausencias de cada certificado'''
    dias_aus = (cert[1] - cert[0]).days + 1
    return dias_aus


def nombrar_dptos(df_ausencias):
    '''Reemplaza los id de los departamentos por sus nombres
    y ordena por cantidad de ausencias'''
    sql = '''SELECT *
        FROM departamentos'''
    _, cur = abrir_bd()
    cur.execute(sql)
    dptos = cur.fetchall()
    cerrar_bd()
    # Dicionario de mapeo
    diccionario_dptos = {dpto[0]: dpto[1] for dpto in dptos}
    # Agregar columna con nombres de departamentos
    df_ausencias['departamento'] = df_ausencias[
        'id_dpto'].map(diccionario_dptos)
    # Borrar la columna de id de departamento
    del df_ausencias['id_dpto']
    return df_ausencias

# %% Hacer graficos


def preparar_base(medidas):
    '''Creo una figura vacia del tamaño buscado'''
    ancho1, alto1 = medidas  # pixeles
    ancho = ancho1 / 100
    alto = alto1 / 100
    fig, ax = plt.subplots(figsize=(ancho, alto))  # en pulgadas
    fig.subplots_adjust(bottom=0.3)
    return fig, ax


def agregar_datos(figura_base, fechas, separ):
    '''Agrega los datos a la figura base'''
    fig, eje = figura_base
    eje_x = fechas['Fecha']
    if separ == 0:  # Ausencias totales
        eje.plot(eje_x, fechas['total_ausencias'],
                 label='Ausencias totales',
                 marker=None, linestyle='-')
    elif separ == 1:  # controlables vs no
        eje.plot(eje_x, fechas['controlables'],
                 label='Ausencias controlables',
                 marker=None, linestyle='-')
        eje.plot(eje_x, fechas['no_controlable'],
                 label='Ausencias no controlables',
                 marker=None, linestyle='-')
    elif separ == 2:  # justificadas vs no
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

# %% Funciones para gráficos por departamento


def preparar_base_dpto(medidas):
    '''Prepara un gráfico base para el gráfico de barras
    por departamento'''
    ancho1, alto1 = medidas  # pixeles
    ancho = ancho1 / 100
    alto = alto1 / 100
    fig, eje = plt.subplots(figsize=(ancho, alto))
    fig.subplots_adjust(bottom=0.3)  # Espacio para eje x
    return fig, eje


def agregar_datos_dpto(figura_base, aus, separ, vista):
    '''Agrega los datos de ausencias por departamento'''
    fig, eje = figura_base
    if vista == 1:  # Porcentaje de ausencias totales
        datos = aus_porc_dpto(aus)
        # Ordenar por porcentaje de ausencias
        aus_ord = datos.sort_values(by='porc_dpto', ascending=False)
        # Mostrar solo departamentos con ausencias
        aus_fil = aus_ord[aus_ord['aus_totales'] > 0]
        eje.bar(aus_fil['departamento'], aus_fil['porc_dpto'],
                label='Ausencias por empleado')

    elif separ == 0:  # Ausencias totales:
        aus['aus_totales'] = aus['justificadas'] +\
            aus['injustificadas'] + aus['incontrolables']
        # Ordenar por ausencias totales
        aus_ord = aus.sort_values(by='aus_totales', ascending=False)
        # Mostrar solo departamentos con ausencias
        aus_fil = aus_ord[aus_ord['aus_totales'] > 0]
        eje.bar(aus_fil['departamento'], aus_fil['aus_totales'],
                label='Ausencias totales')

    elif separ == 1:  # Controlables vs no
        aus['aus_control'] = aus['justificadas'] +\
            aus['injustificadas']
        aus_ord = aus.sort_values(by='aus_control', ascending=False)
        aus_fil = aus_ord[(aus_ord['aus_control'] > 0) |
                          (aus_ord['incontrolables'] > 0)]
        eje.bar(aus_ord['departamento'], aus_ord['aus_control'],
                label='Ausencias controlables')
        eje.bar(aus_ord['departamento'], aus_ord['incontrolables'],
                label='Ausencias no controlables')

    elif separ == 2:  # Justificadas vs no
        eje.bar(aus['departamento'], aus['justificadas'],
                label='Ausencias justificadas')
        eje.bar(aus['departamento'], aus['injustificadas'],
                label='Ausencias injustificadas')
    
    return fig, eje


def poner_eje_x_dpto(fig_con_data, aus):
    '''Fija el título y el eje X del gráfico'''
    fig, eje = fig_con_data
    eje.set_title('Ausencias por Departamento')
    eje.set_xlabel('Departamento')
    eje.tick_params(axis='x', rotation=45)
    for label in eje.get_xticklabels():
        label.set_ha('right')
        label.set_fontsize(8)
    eje.legend()
    return fig, eje


def poner_eje_y_dpto(figura, vista):
    '''Fija el título del eje Y y la forma de
    mostrar los valores para los gráficos de barras de dpto'''
    fig, eje = figura
    if vista == 0:  # Ausencias totales
        eje.set_ylabel('Ausencias totales')
    elif vista == 1:  # Porcentaje de ausencias
        eje.yaxis.set_major_formatter(mtick.PercentFormatter())
        eje.set_ylabel('Porcentaje de ausencias totales')

    return fig, eje


def aus_porc_dpto(aus):
    '''Consulta la cantidad de empleados por departamento
    y calcula el porcentaje de ausencias totales por dpto'''
    sql_e = '''SELECT d.DEPARTAMENTO, COUNT(e.nro_legajo) AS nro_empleados
             FROM departamentos d
             JOIN empleados e
             ON d.id_dep = e.id_dep
             GROUP BY e.id_dep'''
    _, cur = abrir_bd()
    cur.execute(sql_e)
    conteo_empleados = cur.fetchall()
    cerrar_bd()
    # Crear un diccionario de mapeo de empleados por departamento
    empleados_por_dpto = {}
    for departamento in conteo_empleados:
        empleados_por_dpto[departamento[0]] = departamento[1]

    # Agregar a aus la columna nro_empleados con la cantidad de
    # empleados en el departamento correspondiente
    aus['nro_empleados'] = aus['departamento'].map(empleados_por_dpto)
    # Calcular el porcentaje de ausencias totales por dpto
    aus['aus_totales'] = aus['justificadas'] +\
        aus['injustificadas'] + aus['incontrolables']
    aus['porc_dpto'] = aus['aus_totales'] / aus['nro_empleados']
    return aus

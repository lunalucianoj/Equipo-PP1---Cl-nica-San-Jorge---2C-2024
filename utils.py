'''Responsabilidad: Funciones auxiliares que pueden ser reutilizadas en otros scripts.

Contenido:

Funciones para manejar archivos.

Conversión de tipos de datos.

Validación de entradas del usuario.'''

# %% Importacion de modulos

import os
import sqlite3
from database_setup import abrir_bd, cerrar_bd

# %% Funciones auxiliares

def ver_directorio_actual():
    '''Devuelve la carpeta donde esta el modulo'''
    direc = os.path.dirname(os.path.abspath(__file__))
    return direc

def verif_base_datos(base):
    '''Verifica si la base de datos ya fue creada en el
    directorio de trabajo.
    Input: apodo de la base de datos a comprobar
    Output: 1 si la base existe
            2 si la base no existe'''
    direc = ver_directorio_actual()
    ruta_archivo = 'nada'
    if base == 'cert':
        # Revisar si se cargo la base de certificados
        ruta_archivo = os.path.join(direc, 'Ausencias_SJ.db')
        if os.path.isfile(ruta_archivo):
            return 'base_1'
        else:
            return 'base_0'

    elif base == 'empleados':
        # Revisar si se cargo la base de empleados
        try:
            abrir_bd()
            conn, cur = abrir_bd()
            sql = '''SELECT sucursal
                    FROM sucursales'''
            cur.execute(sql)
            dato_empleados = cur.fetchall()
            cerrar_bd()
            return 'base_1'
        except sqlite3.OperationalError:
            return 'base_0'




'''
# Función para contar los días de la semana
def contar_dias_semana(fecha_inicio, duracion):
    if pd.isna(fecha_inicio) or duracion <= 0:  # Verifica fechas no válidas o duraciones incorrectas
        return pd.Series([0]*7)  # Retorna cero para cada día si hay un error
    dias = pd.date_range(fecha_inicio, periods=duracion)
    return dias.weekday.value_counts().reindex(range(7), fill_value=0)

# Aplicar la función a cada fila y expandir los resultados en columnas
dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
conteo_dias = df.apply(lambda row: contar_dias_semana(row['Validez_Desde'], row['Dias']), axis=1)

# Ya que 'conteo_dias' es un DataFrame, lo concatenamos directamente con 'df'
df_con_dias = pd.concat([df, conteo_dias.set_axis(dias_semana, axis=1)], axis=1)


df_con_dias.to_csv('ausencias_por_día.csv', index=False, sep = ';')
'''

# %% Verificaciones de datos de la base
'''
# Agrupa por el nombre y cuenta la cantidad de legajos únicos
inconsistencias = base_df.groupby('Nombre')['Numero_Legajo'].nunique()
inconsistencias_2 = base_df.groupby('Numero_Legajo')['Nombre'].nunique()
# Muestra las filas donde hay más de un legajo para el mismo nombre
inconsistencias_con_legajo_multiple = inconsistencias[inconsistencias > 1]
inconsistencias_c_leg_multiple_2 = inconsistencias_2[inconsistencias_2 > 1]
# Muestra los nombres que tienen más de un número de legajo
print(inconsistencias_con_legajo_multiple)
# Muestra los legajos que tienen más de un nombre
print(inconsistencias_c_leg_multiple_2)

# Verificar si hay números de certificado duplicados
duplicados_certificado = base_df[base_df[
    'Numero_Certificado'].duplicated(keep=False)]
# Muestra los registros donde los números de legajo están repetidos
print(duplicados_certificado)
'''
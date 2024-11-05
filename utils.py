'''Responsabilidad: Funciones auxiliares que pueden ser reutilizadas en otros scripts.

Contenido:

Funciones para manejar archivos.

Conversión de tipos de datos.

Validación de entradas del usuario.'''

# %% Importacion de modulos

import os

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
        ruta_archivo = os.path.join(direc, 'Ausencias_SJ.db')
    elif base == 'empl':
        ruta_archivo = os.path.join(direc, 'Empleados_SJ.db')
    if os.path.isfile(ruta_archivo):
        return 'base_1'
    else:
        return 'base_0'

    
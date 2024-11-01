'''Responsabilidad: Funciones auxiliares que pueden ser reutilizadas en otros scripts.

Contenido:

Funciones para manejar archivos.

Conversión de tipos de datos.

Validación de entradas del usuario.'''

# %% Importacion de modulos

import os

# %% Funciones auxiliares

def ver_directorio_actual():
    direc = os.path.dirname(os.path.abspath(__file__))
    return direc
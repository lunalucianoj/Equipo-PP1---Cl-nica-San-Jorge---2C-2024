'''Responsabilidad: Coordina la ejecución del programa. Importa y llama a funciones de otros scripts según sea necesario.

Contenido: Lógica para iniciar la interfaz de usuario, cargar datos y ejecutar análisis.
'''


import os
import tkinter as tk
from frontend import VentanaPrincipal


def set_working_directory():
    """Set the current working directory to the directory of the script."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():

    set_working_directory()
    app = VentanaPrincipal() # Crea una instancia de VentanaPrincipal

    # Ejecutar la interfaz gráfica
    app.run()


if __name__ == "__main__":
    main()


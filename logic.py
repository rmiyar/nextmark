import os
import datetime
import logging
from db import guardar_marcacion
from tkinter import messagebox

# Configuración de logging
logging.basicConfig(
    filename="marcaciones.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Archivo para guardar el historial local
historial_archivo = "historial_marcaciones.txt"

def validar_datos(usuario, tipo):
    """
    Valida los datos de entrada antes de registrar la marcación.
    """
    if not usuario or not usuario.isalnum():
        raise ValueError("El nombre de usuario debe ser una cadena alfanumérica no vacía.")
    if tipo not in ["entrada", "salida"]:
        raise ValueError("El tipo debe ser 'entrada' o 'salida'.")

def guardar_en_archivo(usuario, tipo, fecha, hora):
    """
    Guarda la marcación en un archivo TXT local.
    """
    try:
        with open(historial_archivo, "a") as archivo:
            archivo.write(f"{usuario},{tipo},{fecha},{hora}\n")
    except Exception as e:
        logging.error(f"Error al escribir en el archivo local: {e}")
        raise

def marcar(usuario, tipo):
    """
    Guarda la marcación en un archivo TXT y en la base de datos.
    """
    ahora = datetime.datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    try:
        # Validación de datos
        validar_datos(usuario, tipo)

        # Guardar en la base de datos
        if guardar_marcacion(usuario, tipo, fecha, hora):
            # Guardar en el archivo local
            guardar_en_archivo(usuario, tipo, fecha, hora)

            # Logging y mensaje de éxito
            logging.info(f"Marcación registrada: Usuario={usuario}, Tipo={tipo}, Fecha={fecha}, Hora={hora}")
            messagebox.showinfo("Éxito", f"Marcación registrada correctamente: {tipo.capitalize()} de {usuario}.")
        else:
            logging.warning("La marcación ya existe o hubo un error en la base de datos.")
            messagebox.showwarning("Advertencia", "La marcación ya existe o hubo un error.")

    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        messagebox.showerror("Error", f"No se pudo registrar la marcación: {e}")

import os
import datetime
import logging
from db import guardar_marcacion
from tkinter import messagebox

# Configuración del archivo de log
LOG_FILE = "marcaciones.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Archivo local para historial de marcaciones
HISTORIAL_ARCHIVO = "historial_marcaciones.txt"

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
        with open(HISTORIAL_ARCHIVO, "a") as archivo:
            archivo.write(f"{usuario},{tipo},{fecha},{hora}\n")
        logging.info(f"Marcación guardada localmente: Usuario={usuario}, Tipo={tipo}, Fecha={fecha}, Hora={hora}")
    except IOError as e:
        logging.error(f"Error al escribir en el archivo local '{HISTORIAL_ARCHIVO}': {e}")
        raise IOError(f"No se pudo guardar la marcación en el archivo local: {e}")

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
            # Manejo cuando no se puede guardar en la base de datos
            logging.warning(f"Marcación duplicada o error en la base de datos para Usuario={usuario}, Tipo={tipo}.")
            messagebox.showwarning(
                "Advertencia",
                "La marcación ya existe o hubo un problema al registrarla en la base de datos."
            )

    except ValueError as ve:
        # Errores de validación
        logging.error(f"Error de validación: {ve}")
        messagebox.showerror("Error de Validación", f"Error: {ve}")

    except IOError as ioe:
        # Errores al guardar en el archivo local
        logging.error(f"Error al guardar en archivo local: {ioe}")
        messagebox.showerror("Error de Archivo", f"Error al guardar localmente: {ioe}")

    except Exception as e:
        # Errores inesperados
        logging.error(f"Error inesperado: {e}")
        messagebox.showerror("Error", f"No se pudo registrar la marcación: {e}")

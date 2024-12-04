import os
import logging
from datetime import datetime, date
from db import guardar_marcacion, obtener_ultima_marcacion
from tkinter import messagebox
from datetime import datetime, timedelta

# Configuración del archivo de log
LOG_FILE = "marcaciones.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Archivo local para historial de marcaciones
HISTORIAL_ARCHIVO = "historial_marcaciones.txt"


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


def determinar_tipo_marcacion(usuario):
    """
    Determina el tipo de marcación (entrada/salida) basado en la última marcación del usuario.
    """
    ultima_marcacion = obtener_ultima_marcacion(usuario)
    fecha_actual = date.today()  # Fecha actual como objeto datetime.date

    print(f"Última marcación obtenida: {ultima_marcacion}")  # Depuración

    if not ultima_marcacion:
        print("No se encontraron marcaciones previas. Primera marcación será 'entrada'.")
        return "entrada"

    ultimo_tipo, ultima_fecha, _ = ultima_marcacion

    if ultima_fecha != fecha_actual:
        print("Última marcación no es del día actual. Marcando como 'entrada'.")
        return "entrada"

    # Alternar entre entrada y salida
    nuevo_tipo = "salida" if ultimo_tipo == "entrada" else "entrada"
    print(f"Última marcación fue '{ultimo_tipo}'. Nueva marcación será '{nuevo_tipo}'.")
    return nuevo_tipo


def marcar(usuario_windows):
    """
    Realiza la marcación automáticamente alternando entre entrada y salida.
    """
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    try:
        # Determinar el tipo de marcación
        tipo = determinar_tipo_marcacion(usuario_windows)

        # Guardar en la base de datos
        if guardar_marcacion(usuario_windows, tipo, fecha, hora):
            # Logging y mensaje de éxito
            logging.info(f"Marcación registrada: Usuario={usuario_windows}, Tipo={tipo}, Fecha={fecha}, Hora={hora}")
            messagebox.showinfo("Éxito", f"Marcación registrada correctamente: {tipo.capitalize()} de {usuario_windows}.")
        else:
            # Manejo cuando no se puede guardar en la base de datos
            logging.warning(f"Marcación duplicada o error en la base de datos para Usuario={usuario_windows}, Tipo={tipo}.")
            messagebox.showwarning(
                "Advertencia",
                "La marcación ya existe o hubo un problema al registrarla en la base de datos."
            )

    except Exception as e:
        # Errores inesperados
        logging.error(f"Error inesperado: {e}")
        messagebox.showerror("Error", f"No se pudo registrar la marcación: {e}")


from datetime import datetime, timedelta
import logging


def calcular_horas_trabajadas(usuario, desde, hasta, marcaciones):
    """
    Calcula las horas trabajadas de un usuario en un rango de fechas dado.
    :param usuario: Nombre del usuario.
    :param desde: Fecha de inicio en formato "YYYY-MM-DD".
    :param hasta: Fecha de fin en formato "YYYY-MM-DD".
    :param marcaciones: Lista de marcaciones obtenidas de la base de datos.
    :return: Tupla (total_horas, total_minutos).
    """
    try:
        # Validar fechas
        desde_fecha = datetime.strptime(desde, "%Y-%m-%d")
        hasta_fecha = datetime.strptime(hasta, "%Y-%m-%d")

        # Calcular horas trabajadas
        total_horas = timedelta()
        entrada_actual = None

        for registro in marcaciones:
            tipo = registro[1]  # Tipo de marcación ("entrada" o "salida")
            fecha = registro[2]  # Fecha (YYYY-MM-DD)
            hora = registro[3]  # Hora (HH:MM:SS)

            # Combinar fecha y hora en un solo objeto datetime
            fecha_hora = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S")

            if tipo == "entrada":
                entrada_actual = fecha_hora
            elif tipo == "salida" and entrada_actual:
                total_horas += fecha_hora - entrada_actual
                entrada_actual = None

        # Convertir timedelta a horas y minutos
        horas, resto = divmod(total_horas.total_seconds(), 3600)
        minutos = resto // 60
        return int(horas), int(minutos)
    except Exception as e:
        logging.error(f"Error al calcular horas trabajadas: {e}")
        raise

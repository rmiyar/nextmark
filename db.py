import psycopg2
import uuid
from datetime import datetime
import os
import configparser

# Configuración de conexión a la base de datos
db_config = {
    "dbname": "postgres",
    "user": "postgres.wzqrdlomiherqivaegho",
    "password": "53kkMYf!PDc$sHG",  # Reemplaza con tu contraseña
    "host": "aws-0-us-west-1.pooler.supabase.com",
    "port": 6543
}

def leer_usuario_config():
    """
    Lee los datos del usuario desde config.ini.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        nombre = config["USUARIO"]["nombre"]
        apellido = config["USUARIO"]["apellido"]
        return nombre, apellido
    except KeyError as e:
        print(f"Error al leer el archivo de configuración: {e}")
        return None, None

def conectar_bd():
    """
    Establece una conexión con la base de datos.
    """
    try:
        connection = psycopg2.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def guardar_marcacion(user_windows, tipo, fecha, hora):
    """
    Guarda una marcación en la base de datos.
    Relaciona la marcación con el usuario basado en los datos de config.ini.
    """
    connection = conectar_bd()
    if not connection:
        return False  # No se pudo conectar a la base de datos

    try:
        # Leer los datos del usuario desde config.ini
        nombre, apellido = leer_usuario_config()

        if not nombre or not apellido:
            print("No se encontraron datos válidos en config.ini.")
            return False

        # Obtener usuario_id y nombre_completo de la tabla users
        query_usuario = """
        SELECT id, CONCAT(nombre, ' ', apellido) AS nombre_completo
        FROM users
        WHERE nombre = %s AND apellido = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query_usuario, (nombre, apellido))
            usuario_data = cursor.fetchone()

        # Validar si se obtuvo un usuario
        if not usuario_data:
            print(f"No se encontró el usuario con nombre: {nombre} y apellido: {apellido}")
            return False  # Detener si no se encuentra el usuario

        usuario_id, nombre_completo = usuario_data
        print(f"Usuario encontrado: usuario_id={usuario_id}, nombre_completo={nombre_completo}")

        # Insertar la marcación en historial_marcaciones
        query_marcacion = """
        INSERT INTO historial_marcaciones (usuario_id, user_windows, nombre_completo, fecha, hora_entrada, tipo_marcacion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with connection.cursor() as cursor:
            # Depuración: Imprimir los valores antes de ejecutar
            print(f"Insertando: usuario_id={usuario_id}, user_windows={user_windows}, nombre_completo={nombre_completo}, fecha={fecha}, hora={hora}, tipo={tipo}")
            cursor.execute(query_marcacion, (usuario_id, user_windows, nombre_completo, fecha, hora, tipo))
        connection.commit()
        print(f"Marcación guardada en la base de datos: {user_windows}, {tipo}, {fecha}, {hora}")
        return True
    except Exception as e:
        print(f"Error al guardar la marcación: {e}")
        return False
    finally:
        connection.close()



def obtener_marcaciones():
    """
    Consulta todas las marcaciones desde la base de datos PostgreSQL.
    """
    connection = conectar_bd()
    if not connection:
        return []  # Devuelve una lista vacía si no se puede conectar

    try:
        query = """
        SELECT nombre_usuario, tipo_marcacion, fecha, hora_entrada 
        FROM historial_marcaciones 
        ORDER BY fecha DESC, hora_entrada DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
        return []
    finally:
        connection.close()


def obtener_marcaciones_filtradas(usuario=None, tipo=None, dia=None):
    """
    Consulta marcaciones desde la base de datos aplicando filtros.
    """
    connection = conectar_bd()
    if not connection:
        return []

    # Convertir cadenas vacías a None
    usuario = usuario.strip() if usuario and usuario.strip() else None
    tipo = tipo.strip() if tipo and tipo.strip() else None
    dia = dia.strip() if dia and dia.strip() else None

    # Convertir el formato de fecha de DD-MM-YYYY a YYYY-MM-DD
    if dia:
        try:
            dia = datetime.strptime(dia, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Formato de fecha inválido: {dia}. Use DD-MM-YYYY.")
            dia = None

    try:
        query = """
        SELECT nombre_usuario, tipo_marcacion, fecha, hora_entrada
        FROM historial_marcaciones
        WHERE (%s IS NULL OR nombre_usuario = %s)
          AND (%s IS NULL OR tipo_marcacion = %s)
          AND (%s IS NULL OR fecha = %s)
        ORDER BY fecha DESC, hora_entrada DESC;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (usuario, usuario, tipo, tipo, dia, dia))
            resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al consultar la base de datos con filtros: {e}")
        return []
    finally:
        connection.close()


def registrar_usuario(nombre, apellido):
    """
    Registra un usuario en la tabla users.
    El campo "user" será el nombre del usuario de Windows actualmente logueado.
    """
    connection = conectar_bd()
    if not connection:
        return False  # No se pudo conectar a la base de datos

    try:
        # Obtener el usuario actual de Windows
        user = os.getlogin()

        # Verificar si el usuario ya existe
        verificar_query = "SELECT id FROM users WHERE nombre = %s AND apellido = %s AND user = %s"
        with connection.cursor() as cursor:
            cursor.execute(verificar_query, (nombre, apellido, user))
            resultado = cursor.fetchone()

        if resultado:
            print(f"El usuario {nombre} {apellido} con el usuario del sistema {user} ya está registrado.")
            return True  # El usuario ya existe, no se hace nada

        # Registrar un nuevo usuario
        registrar_query = """
        INSERT INTO users (nombre, apellido, "user")
        VALUES (%s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(registrar_query, (nombre, apellido, user))
        connection.commit()
        print(f"Usuario registrado exitosamente: {nombre} {apellido} ({user})")
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False
    finally:
        connection.close()

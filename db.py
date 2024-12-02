import psycopg2
import uuid
from datetime import datetime
import os
import configparser
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de conexión a la base de datos
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT"))
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
        return False

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

        if not usuario_data:
            print(f"No se encontró el usuario con nombre: {nombre} y apellido: {apellido}")
            return False

        usuario_id, nombre_completo = usuario_data
        print(f"Usuario encontrado: usuario_id={usuario_id}, nombre_completo={nombre_completo}")

        # Insertar la marcación en historial_marcaciones
        query_marcacion = """
        INSERT INTO historial_marcaciones (usuario_id, user_windows, nombre_completo, fecha, hora_entrada, tipo_marcacion)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with connection.cursor() as cursor:
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
        return []

    try:
        query = """
        SELECT nombre_completo, tipo_marcacion, fecha, hora_entrada 
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

    usuario = usuario.strip() if usuario else None
    tipo = tipo.strip() if tipo else None
    dia = dia.strip() if dia else None

    if dia:
        try:
            dia = datetime.strptime(dia, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Formato de fecha inválido: {dia}. Use DD-MM-YYYY.")
            dia = None

    try:
        query = """
        SELECT nombre_completo, tipo_marcacion, fecha, hora_entrada
        FROM historial_marcaciones
        WHERE (%s IS NULL OR LOWER(nombre_completo) LIKE LOWER(%s))
          AND (%s IS NULL OR tipo_marcacion = %s)
          AND (%s IS NULL OR fecha = %s)
        ORDER BY fecha DESC, hora_entrada DESC;
        """
        with connection.cursor() as cursor:
            like_usuario = f"%{usuario}%" if usuario else None
            cursor.execute(query, (usuario, like_usuario, tipo, tipo, dia, dia))
            resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al consultar la base de datos con filtros: {e}")
        return []
    finally:
        connection.close()

def registrar_usuario(nombre, apellido, user_windows):
    """
    Registra un usuario en la tabla `users`.
    """
    connection = conectar_bd()
    if not connection:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return False

    try:
        # Convertir nombre y apellido a mayúsculas
        nombre = nombre.upper()
        apellido = apellido.upper()

        # Verificar si el usuario ya existe
        verificar_query = "SELECT id FROM users WHERE user_windows = %s"
        with connection.cursor() as cursor:
            cursor.execute(verificar_query, (user_windows,))
            resultado = cursor.fetchone()

        if resultado:
            print(f"El usuario {user_windows} ya está registrado con ID {resultado[0]}.")
            return True  # Si ya existe, no se hace nada

        # Registrar un nuevo usuario
        registrar_query = """
        INSERT INTO users (nombre, apellido, user_windows)
        VALUES (%s, %s, %s) RETURNING id
        """
        with connection.cursor() as cursor:
            print(f"Registrando usuario: {nombre} {apellido} ({user_windows})")
            cursor.execute(registrar_query, (nombre, apellido, user_windows))
            user_id = cursor.fetchone()[0]
            connection.commit()

        print(f"Usuario registrado exitosamente con ID {user_id}.")
        return True
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        return False
    finally:
        connection.close()



def asignar_a_grupo(user_windows, group_name="Usuarios"):
    """
    Asigna un usuario al grupo especificado.
    Crea el grupo si no existe y asegura que solo se asigne una vez.
    """
    connection = conectar_bd()
    if not connection:
        print("Error: No se pudo establecer conexión con la base de datos.")
        return False

    try:
        # Obtener el usuario ID
        query_usuario = "SELECT id FROM users WHERE user_windows = %s"
        with connection.cursor() as cursor:
            cursor.execute(query_usuario, (user_windows,))
            usuario = cursor.fetchone()

        if not usuario:
            print(f"Usuario con user_windows={user_windows} no encontrado.")
            return False

        user_id = usuario[0]

        # Verificar si el grupo existe
        query_grupo = "SELECT id FROM groups WHERE nombre = %s"
        with connection.cursor() as cursor:
            cursor.execute(query_grupo, (group_name,))
            grupo = cursor.fetchone()

        if not grupo:
            # Crear el grupo si no existe
            query_crear_grupo = "INSERT INTO groups (nombre) VALUES (%s) RETURNING id"
            with connection.cursor() as cursor:
                cursor.execute(query_crear_grupo, (group_name,))
                group_id = cursor.fetchone()[0]
                connection.commit()
        else:
            group_id = grupo[0]

        # Verificar si el usuario ya está asignado al grupo
        query_asignacion = "SELECT 1 FROM user_groups WHERE user_id = %s AND group_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query_asignacion, (user_id, group_id))
            asignacion = cursor.fetchone()

        if asignacion:
            print(f"Usuario {user_id} ya está asignado al grupo '{group_name}'.")
            return True

        # Asignar el usuario al grupo
        query_asignar = "INSERT INTO user_groups (user_id, group_id) VALUES (%s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query_asignar, (user_id, group_id))
            connection.commit()

        print(f"Usuario {user_id} asignado al grupo '{group_name}'.")
        return True
    except Exception as e:
        print(f"Error al asignar usuario al grupo: {e}")
        return False
    finally:
        connection.close()


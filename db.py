import psycopg2
import uuid
from datetime import datetime
import os
import configparser
from dotenv import load_dotenv
import sys

def resource_path(relative_path):
    """Devuelve la ruta correcta, ya sea en desarrollo o en un ejecutable."""
    if hasattr(sys, "_MEIPASS"):  # PyInstaller almacena recursos en `_MEIPASS`
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Cargar variables de entorno desde .env
env_path = resource_path(".env")
load_dotenv(env_path)

# Configuración de conexión a la base de datos
db_config = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT"))
}


def conectar_bd():
    """
    Establece una conexión con la base de datos.
    """
    try:
        print(f"Intentando conectar con la base de datos usando: {db_config}")
        connection = psycopg2.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def guardar_marcacion(user_windows, tipo, fecha, hora):
    """
    Guarda una marcación en la base de datos asociada al usuario correspondiente.
    """
    connection = conectar_bd()
    if not connection:
        return False

    try:
        # Verificar si el usuario existe y obtener su información
        query_usuario = """
        SELECT id, CONCAT(nombre, ' ', apellido) AS nombre_completo
        FROM users
        WHERE user_windows = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query_usuario, (user_windows,))
            usuario_data = cursor.fetchone()

        if not usuario_data:
            print(f"Usuario con user_windows={user_windows} no encontrado.")
            return False

        usuario_id, nombre_completo = usuario_data

        # Insertar la nueva marcación
        query_marcacion = """
        INSERT INTO historial_marcaciones (usuario_id, user_windows, nombre_completo, tipo_marcacion, fecha, hora_entrada)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with connection.cursor() as cursor:
            cursor.execute(query_marcacion, (usuario_id, user_windows, nombre_completo, tipo, fecha, hora))
        connection.commit()
        print(f"Marcación guardada: {user_windows}, {tipo}, {fecha}, {hora}")
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
            # Validar que la fecha está en el formato correcto (YYYY-MM-DD)
            datetime.strptime(dia, "%Y-%m-%d")
        except ValueError:
            print(f"Formato de fecha inválido: {dia}. Use YYYY-MM-DD.")
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



def obtener_marcaciones_admin(usuario=None, tipo=None, desde=None, hasta=None):
    """
    Obtiene las marcaciones filtradas con privilegios de administrador.
    Permite filtrar por usuario, tipo de marcación y rango de fechas.
    """
    connection = conectar_bd()
    if not connection:
        return []

    try:
        query = """
        SELECT 
            CONCAT(u.nombre, ' ', u.apellido) AS nombre_completo, 
            h.tipo_marcacion, 
            h.fecha, 
            h.hora_entrada
        FROM historial_marcaciones h
        JOIN users u ON h.usuario_id = u.id
        WHERE 1=1
        """
        parametros = []

        # Filtrar por usuario
        if usuario:
            query += " AND CONCAT(u.nombre, ' ', u.apellido) = %s"
            parametros.append(usuario)

        # Filtrar por tipo de marcación
        if tipo:
            query += " AND h.tipo_marcacion = %s"
            parametros.append(tipo)

        # Convertir fechas al formato esperado por la base de datos (YYYY-MM-DD)
        if desde and hasta:
            try:
                # Las fechas ya vienen en el formato correcto
                query += " AND h.fecha BETWEEN %s AND %s"
                parametros.extend([desde, hasta])
            except ValueError:
                print("Error: Las fechas no tienen el formato correcto (DD-MM-YYYY).")
                return []

        # Imprimir la consulta SQL y los parámetros para depuración
        print("Consulta SQL generada:")
        print(query)
        print("Parámetros:")
        print(parametros)

        with connection.cursor() as cursor:
            cursor.execute(query, parametros)
            resultados = cursor.fetchall()

        return resultados
    except Exception as e:
        print(f"Error al obtener marcaciones para administrador: {e}")
        return []
    finally:
        connection.close()


def registrar_usuario(nombre, apellido, user_windows, group_name="Usuarios"):
    """
    Registra un usuario en la tabla `users` y lo asigna a un grupo solo si es la primera vez.
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

        # Asignar al grupo solo si es la primera vez
        if not asignar_a_grupo(user_windows, group_name):
            print(f"No se pudo asignar al grupo {group_name}. Verifique la base de datos.")

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

def obtener_ultima_marcacion(usuario_windows):
    """
    Obtiene la última marcación del usuario desde la tabla historial_marcaciones.
    """
    connection = conectar_bd()
    if not connection:
        return None

    try:
        query = """
        SELECT tipo_marcacion, fecha, hora_entrada
        FROM historial_marcaciones
        WHERE user_windows = %s
        ORDER BY fecha DESC, hora_entrada DESC
        LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (usuario_windows,))
            return cursor.fetchone()  # Devuelve la última marcación o None
    except Exception as e:
        print(f"Error al obtener la última marcación: {e}")
        return None
    finally:
        connection.close()


def es_primera_vez_usuario(user_windows):
    """
    Verifica si el usuario de Windows ya está registrado en la base de datos.
    """
    connection = conectar_bd()
    if not connection:
        print("Error al conectar con la base de datos.")
        return False

    try:
        query = "SELECT 1 FROM users WHERE user_windows = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, (user_windows,))
            resultado = cursor.fetchone()
        return resultado is None  # Si no hay resultados, es la primera vez
    except Exception as e:
        print(f"Error al verificar usuario en la base de datos: {e}")
        return False
    finally:
        connection.close()


def autenticar_administrador(user_windows, password):
    """
    Verifica si un usuario es administrador y sus credenciales son válidas.
    """
    connection = conectar_bd()
    if not connection:
        return False

    try:
        query = """
        SELECT u.id
        FROM users u
        INNER JOIN user_groups ug ON u.id = ug.user_id
        INNER JOIN groups g ON ug.group_id = g.id
        WHERE u.user_windows = %s AND u.contraseña = %s AND g.nombre = 'Administradores';
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (user_windows, password))
            resultado = cursor.fetchone()

        return resultado is not None
    except Exception as e:
        print(f"Error al autenticar administrador: {e}")
        return False
    finally:
        connection.close()

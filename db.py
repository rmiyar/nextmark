import psycopg2
import uuid
from datetime import datetime

# Configuración de conexión a la base de datos
db_config = {
    "dbname": "postgres",
    "user": "postgres.wzqrdlomiherqivaegho",
    "password": "53kkMYf!PDc$sHG",  # Reemplaza con tu contraseña
    "host": "aws-0-us-west-1.pooler.supabase.com",
    "port": 6543
}

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


def guardar_marcacion(usuario, tipo, fecha, hora):
    """
    Guarda una marcación en la base de datos.
    """
    connection = conectar_bd()
    if not connection:
        return False  # No se pudo conectar a la base de datos

    try:
        usuario_id = str(uuid.uuid4())  # Genera un UUID único para el usuario
        query = """
        INSERT INTO historial_marcaciones (usuario_id, nombre_usuario, fecha, hora_entrada, tipo_marcacion)
        VALUES (%s, %s, %s, %s, %s);
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (usuario_id, usuario, fecha, hora, tipo))
        connection.commit()
        print(f"Marcación guardada en la base de datos: {usuario}, {tipo}, {fecha}, {hora}")
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

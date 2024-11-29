import uuid
import datetime
from db import conectar_bd, guardar_marcacion, cargar_historial

def probar_conexion():
    """
    Prueba si la conexión con la base de datos es exitosa.
    """
    connection = conectar_bd()
    if connection:
        print("Conexión a la base de datos exitosa.")
        connection.close()
    else:
        print("Error al conectar a la base de datos.")

def probar_guardar_marcacion():
    """
    Prueba la función para guardar una marcación en la base de datos.
    """
    usuario_id = str(uuid.uuid4())  # Genera un UUID válido
    nombre_usuario = "test_user"
    tipo = "entrada"
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    # Ajusta la función guardar_marcacion para que acepte UUID
    connection = conectar_bd()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return

    try:
        query = """
        INSERT INTO historial_marcaciones (usuario_id, nombre_usuario, fecha, hora_entrada, tipo_marcacion)
        VALUES (%s, %s, %s, %s, %s);
        """
        with connection.cursor() as cursor:
            cursor.execute(query, (usuario_id, nombre_usuario, fecha, hora, tipo))
        connection.commit()
        print(f"Marcación guardada correctamente en la base de datos con usuario_id: {usuario_id}")
    except Exception as e:
        print(f"Error al guardar la marcación: {e}")
    finally:
        connection.close()

def probar_cargar_historial():
    """
    Prueba la función para cargar el historial de marcaciones desde la base de datos.
    """
    connection = conectar_bd()
    if not connection:
        print("No se pudo conectar a la base de datos.")
        return

    try:
        query = "SELECT usuario_id, nombre_usuario, fecha, hora_entrada, tipo_marcacion FROM historial_marcaciones;"
        with connection.cursor() as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
        if resultados:
            print("Historial cargado exitosamente:")
            for registro in resultados:
                print(registro)
        else:
            print("No se encontraron registros en el historial.")
    except Exception as e:
        print(f"Error al cargar el historial: {e}")
    finally:
        connection.close()

# Llamar las funciones de prueba
if __name__ == "__main__":
    print("Prueba de conexión:")
    probar_conexion()

    print("\nPrueba de guardar marcación:")
    probar_guardar_marcacion()

    print("\nPrueba de cargar historial:")
    probar_cargar_historial()

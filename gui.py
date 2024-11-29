import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import configparser
from config import COLOR_FONDO
from user_screen import mostrar_pantalla_usuario
from admin_screen import mostrar_pantalla_administrador
from db import registrar_usuario 


def es_primera_vez():
    """
    Verifica si es la primera vez que se abre el programa y actualiza el valor después de completar la configuración.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = configparser.ConfigParser()

    # Si el archivo no existe, lo crea con primera_vez=true
    if not os.path.exists(config_path):
        config["GENERAL"] = {"primera_vez": "true"}
        with open(config_path, "w") as configfile:
            config.write(configfile)
        return True

    # Leer el archivo existente
    config.read(config_path)
    primera_vez = config["GENERAL"].get("primera_vez", "true")

    # Si es la primera vez, solicitar datos y actualizar
    if primera_vez == "true":
        solicitar_datos_usuario(config, config_path)
        return True

    return False



def solicitar_datos_usuario(config, config_path):
    """
    Solicita el nombre y apellido del usuario y los guarda en el archivo de configuración.
    Actualiza el valor de `primera_vez` a `false` inmediatamente después de registrar los datos.
    """
    nombre = simpledialog.askstring("Primera Configuración", "Ingrese su nombre:")
    if not nombre:
        messagebox.showwarning("Advertencia", "Debe ingresar un nombre válido.")
        return solicitar_datos_usuario(config, config_path)

    apellido = simpledialog.askstring("Primera Configuración", "Ingrese su apellido:")
    if not apellido:
        messagebox.showwarning("Advertencia", "Debe ingresar un apellido válido.")
        return solicitar_datos_usuario(config, config_path)

    # Registrar al usuario en la base de datos
    if registrar_usuario(nombre, apellido):
        print(f"Usuario {nombre} {apellido} registrado correctamente en la base de datos.")
    else:
        print(f"Error al registrar el usuario {nombre} {apellido} en la base de datos.")

    # Guardar los datos del usuario en el archivo de configuración
    guardar_datos_usuario(config, config_path, nombre, apellido)

    # Actualizar `primera_vez` a false
    config["GENERAL"]["primera_vez"] = "false"
    with open(config_path, "w") as configfile:
        config.write(configfile)

    print("Configuración inicial completada. `primera_vez` ahora es false.")
    messagebox.showinfo("Bienvenido", f"¡Hola {nombre} {apellido}, bienvenido al sistema!")

def guardar_datos_usuario(config, config_path, nombre, apellido):
    """
    Guarda el nombre y apellido del usuario en el archivo de configuración.
    """
    if "USUARIO" not in config:
        config["USUARIO"] = {}
    config["USUARIO"]["nombre"] = nombre
    config["USUARIO"]["apellido"] = apellido

    # Sobrescribir el archivo con los nuevos datos
    with open(config_path, "w") as configfile:
        config.write(configfile)
    print(f"Datos guardados: Nombre={nombre}, Apellido={apellido}")

def acceder_como_usuario(root, volver_pantalla_inicial):
    """
    Lógica para el acceso como usuario.
    Verifica si es la primera vez que se abre el programa.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = configparser.ConfigParser()

    # Verificar si es la primera vez
    if not os.path.exists(config_path):
        config["GENERAL"] = {"primera_vez": "true"}
        with open(config_path, "w") as configfile:
            config.write(configfile)

    config.read(config_path)
    primera_vez = config["GENERAL"].get("primera_vez", "true")

    if primera_vez == "true":
        # Pasar los argumentos a solicitar_datos_usuario
        solicitar_datos_usuario(config, config_path)

    # Mostrar la pantalla de usuario
    mostrar_pantalla_usuario(root, volver_pantalla_inicial)



def iniciar_aplicacion():
    root = tk.Tk()
    root.title("Sistema de Marcación - NEXEL")
    root.geometry("900x700")
    root.configure(bg=COLOR_FONDO)  # Usar el color de fondo compartido

    # Ruta del archivo `admkey`
    ADMKEY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admkey")

    # Función para validar el acceso del administrador
    def validar_acceso_administrador():
        # Verificar si el archivo `admkey` existe
        if not os.path.exists(ADMKEY_PATH):
            messagebox.showerror(
                "Acceso Denegado",
                "No se encontró el archivo 'admkey' en la ubicación del programa.\n"
                "Consulte con el administrador.",
            )
            return

        # Leer la contraseña almacenada en el archivo `admkey`
        try:
            with open(ADMKEY_PATH, "r") as archivo:
                contraseña_almacenada = archivo.read().strip()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo 'admkey': {e}")
            return

        # Solicitar la contraseña al usuario
        contraseña_ingresada = simpledialog.askstring(
            "Acceso Administrador", "Ingrese la contraseña para continuar:", show="*"
        )

        if contraseña_ingresada is None:  # El usuario presionó cancelar
            return

        # Comparar la contraseña ingresada con la almacenada
        if contraseña_ingresada == contraseña_almacenada:
            mostrar_pantalla_administrador(root, mostrar_pantalla_inicial)
        else:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta. Intente nuevamente.")

    def mostrar_pantalla_inicial():
        for widget in root.winfo_children():
            widget.destroy()

        frame = tk.Frame(root, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        titulo = tk.Label(
            frame,
            text="Bienvenido al Sistema de Marcación - NEXEL",
            font=("Arial", 24, "bold"),
            bg=COLOR_FONDO,
            fg="#333",
        )
        titulo.pack(pady=40)

        btn_usuario = tk.Button(
            frame,
            text="Acceder como Usuario",
            bg="#4caf50",
            fg="white",
            font=("Arial", 14, "bold"),
            command=lambda: acceder_como_usuario(root, mostrar_pantalla_inicial),
            width=25,
            relief="flat",
        )
        btn_usuario.pack(pady=15)

        btn_admin = tk.Button(
            frame,
            text="Acceder como Administrador",
            bg="#1976d2",
            fg="white",
            font=("Arial", 14, "bold"),
            command=validar_acceso_administrador,  # Validar archivo y contraseña
            width=25,
            relief="flat",
        )
        btn_admin.pack(pady=15)

        footer = tk.Label(
            frame,
            text="© 2024 NEXEL - Sistema de Marcación",
            font=("Arial", 10),
            bg=COLOR_FONDO,
            fg="#333",
        )
        footer.pack(side="bottom", pady=20)

    mostrar_pantalla_inicial()
    root.mainloop()

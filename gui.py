import tkinter as tk
from tkinter import simpledialog, messagebox
import os
import configparser
from config import COLOR_FONDO
from user_screen import mostrar_pantalla_usuario
from admin_screen import mostrar_pantalla_administrador
from db import registrar_usuario, asignar_a_grupo, conectar_bd


def inicializar_configuracion(config_path):
    """
    Inicializa el archivo config.ini con los valores predeterminados si no existe
    o si le faltan claves/secciones necesarias.
    """
    config = configparser.ConfigParser()

    if not os.path.exists(config_path):
        print("Archivo config.ini no encontrado. Creando uno nuevo...")
        config["GENERAL"] = {"primera_vez": "true"}
        config["USUARIO"] = {"nombre": "", "apellido": ""}
    else:
        config.read(config_path)
        if "GENERAL" not in config:
            config["GENERAL"] = {"primera_vez": "true"}
        if "USUARIO" not in config:
            config["USUARIO"] = {"nombre": "", "apellido": ""}
        if "primera_vez" not in config["GENERAL"]:
            config["GENERAL"]["primera_vez"] = "true"

    with open(config_path, "w") as configfile:
        config.write(configfile)
    return config


def es_primera_vez(config, config_path):
    """
    Verifica si es la primera vez que se abre el programa y actualiza el valor
    después de completar la configuración.
    """
    primera_vez = config["GENERAL"].get("primera_vez", "true")
    if primera_vez == "true":
        solicitar_datos_usuario(config, config_path)
        return True
    return False


def solicitar_datos_usuario(config, config_path):
    """
    Solicita el nombre y apellido del usuario en un mismo diálogo.
    """
    def confirmar_datos():
        """
        Valida y guarda los datos ingresados.
        """
        nombre = entry_nombre.get().strip()
        apellido = entry_apellido.get().strip()

        if not nombre.isalpha():
            messagebox.showwarning("Advertencia", "El nombre debe ser solo letras.")
            return
        if not apellido.isalpha():
            messagebox.showwarning("Advertencia", "El apellido debe ser solo letras.")
            return

        # Registrar al usuario
        user_windows = os.getlogin()
        if registrar_usuario(nombre, apellido, user_windows):
            guardar_datos_usuario(config, config_path, nombre, apellido)
            config["GENERAL"]["primera_vez"] = "false"
            with open(config_path, "w") as configfile:
                config.write(configfile)
            messagebox.showinfo("Bienvenido", f"¡Hola {nombre} {apellido}, bienvenido al sistema!")
            ventana.destroy()
        else:
            messagebox.showerror("Error", f"El usuario {nombre} {apellido} no pudo ser registrado.")

    def cancelar():
        """
        Cierra la ventana sin guardar nada.
        """
        ventana.destroy()

    # Crear ventana emergente
    ventana = tk.Toplevel()
    ventana.title("Configuración Inicial")
    ventana.geometry("400x250")
    ventana.configure(bg=COLOR_FONDO)
    ventana.grab_set()  # Bloquear interacción con la ventana principal

    tk.Label(ventana, text="Ingrese su nombre y apellido:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10)

    # Campo de entrada para el nombre
    tk.Label(ventana, text="Nombre:", font=("Arial", 10), bg=COLOR_FONDO).pack(anchor="w", padx=20)
    entry_nombre = tk.Entry(ventana, font=("Arial", 12))
    entry_nombre.pack(padx=20, pady=5, fill="x")
    entry_nombre.focus()

    # Campo de entrada para el apellido
    tk.Label(ventana, text="Apellido:", font=("Arial", 10), bg=COLOR_FONDO).pack(anchor="w", padx=20)
    entry_apellido = tk.Entry(ventana, font=("Arial", 12))
    entry_apellido.pack(padx=20, pady=5, fill="x")

    # Botones OK y Cancelar
    botones_frame = tk.Frame(ventana, bg=COLOR_FONDO)
    botones_frame.pack(pady=10)

    tk.Button(botones_frame, text="OK", font=("Arial", 12), command=confirmar_datos, bg="#4caf50", fg="white").pack(side="left", padx=10)
    tk.Button(botones_frame, text="Cancelar", font=("Arial", 12), command=cancelar, bg="#f44336", fg="white").pack(side="right", padx=10)

    ventana.mainloop()



def acceder_como_usuario(root, volver_pantalla_inicial):
    """
    Lógica para el acceso como usuario.
    Verifica si es la primera vez y asigna al grupo "Usuarios" automáticamente solo en esa ocasión.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = inicializar_configuracion(config_path)

    # Verifica si es la primera vez
    if es_primera_vez(config, config_path):
        # Durante la primera vez, el registro y asignación ya se manejan en solicitar_datos_usuario
        return

    # Usuario ya registrado, simplemente mostrar la pantalla de usuario
    print(f"Usuario actual de Windows: {os.getlogin()}")

    # Mostrar la pantalla de usuario sin intentar asignar al grupo nuevamente
    mostrar_pantalla_usuario(root, volver_pantalla_inicial)




def guardar_datos_usuario(config, config_path, nombre, apellido):
    """
    Guarda el nombre y apellido del usuario en el archivo de configuración.
    """
    if "USUARIO" not in config:
        config["USUARIO"] = {}
    config["USUARIO"]["nombre"] = nombre
    config["USUARIO"]["apellido"] = apellido

    with open(config_path, "w") as configfile:
        config.write(configfile)
    print(f"Datos guardados: Nombre={nombre}, Apellido={apellido}")


def acceder_como_usuario(root, volver_pantalla_inicial):
    """
    Lógica para el acceso como usuario.
    Verifica si es la primera vez y asigna al grupo "Usuarios" automáticamente.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config = inicializar_configuracion(config_path)

    if es_primera_vez(config, config_path):
        return

    # Leer el usuario actual desde config.ini
    user_windows = os.getlogin()
    if not user_windows:
        messagebox.showerror("Error", "No se pudo determinar el usuario de Windows.")
        return

    print(f"Usuario actual de Windows: {user_windows}")  # Depuración


    # Mostrar la pantalla de usuario
    mostrar_pantalla_usuario(root, volver_pantalla_inicial)


def validar_acceso_administrador(root, mostrar_pantalla_inicial):
    """
    Valida el acceso del administrador verificando usuario y contraseña en la base de datos.
    """

    def autenticar_usuario(usuario, contraseña):
        """
        Autentica al usuario administrador en la base de datos.
        """
        connection = conectar_bd()
        if not connection:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return False

        try:
            query = """
            SELECT u.id, u.user_windows, u.contraseña
            FROM users u
            INNER JOIN user_groups ug ON u.id = ug.user_id
            INNER JOIN groups g ON ug.group_id = g.id
            WHERE u.user_windows = %s 
            AND (u.contraseña = %s OR u.contraseña IS NULL)
            AND g.nombre = 'Administradores';
            """
            with connection.cursor() as cursor:
                cursor.execute(query, (usuario, contraseña))
                resultado = cursor.fetchone()

            if resultado:
                return True
            return False
        except Exception as e:
            print(f"Error al autenticar al usuario: {e}")
            return False
        finally:
            connection.close()

    # Crear ventana emergente para solicitar credenciales
    ventana = tk.Toplevel(root)
    ventana.title("Acceso Administrador")
    ventana.geometry("400x250")
    ventana.configure(bg=COLOR_FONDO)
    ventana.grab_set()  # Bloquear interacción con la ventana principal

    tk.Label(ventana, text="Usuario:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10, anchor="w", padx=20)
    entry_usuario = tk.Entry(ventana, font=("Arial", 12))
    entry_usuario.pack(padx=20, pady=5, fill="x")

    tk.Label(ventana, text="Contraseña:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10, anchor="w", padx=20)
    entry_contraseña = tk.Entry(ventana, font=("Arial", 12), show="*")
    entry_contraseña.pack(padx=20, pady=5, fill="x")

    def intentar_acceso():
        """
        Intenta autenticar al usuario administrador.
        """
        usuario = entry_usuario.get().strip()
        contraseña = entry_contraseña.get().strip()

        if not usuario:
            messagebox.showwarning("Advertencia", "Debe ingresar un usuario.")
            return

        if autenticar_usuario(usuario, contraseña):
            ventana.destroy()
            mostrar_pantalla_administrador(root, mostrar_pantalla_inicial)
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")

    # Botones
    tk.Button(
        ventana,
        text="Ingresar",
        font=("Arial", 12),
        command=intentar_acceso,
        bg="#4caf50",
        fg="white",
    ).pack(side="left", padx=10, pady=20)

    tk.Button(
        ventana,
        text="Cancelar",
        font=("Arial", 12),
        command=ventana.destroy,
        bg="#f44336",
        fg="white",
    ).pack(side="right", padx=10, pady=20)

    ventana.mainloop()



    # Crear ventana emergente para solicitar credenciales
    ventana = tk.Toplevel(root)
    ventana.title("Acceso Administrador")
    ventana.geometry("400x200")
    ventana.configure(bg=COLOR_FONDO)
    ventana.grab_set()  # Bloquea interacción con la ventana principal

    tk.Label(ventana, text="Usuario:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=5, anchor="w", padx=20)
    entry_usuario = tk.Entry(ventana, font=("Arial", 12))
    entry_usuario.pack(padx=20, pady=5, fill="x")

    tk.Label(ventana, text="Contraseña:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=5, anchor="w", padx=20)
    entry_contraseña = tk.Entry(ventana, font=("Arial", 12), show="*")
    entry_contraseña.pack(padx=20, pady=5, fill="x")

    def intentar_acceso():
        """
        Intenta autenticar al usuario administrador.
        """
        usuario = entry_usuario.get().strip()
        contraseña = entry_contraseña.get().strip()

        if not usuario or not contraseña:
            messagebox.showwarning("Advertencia", "Debe ingresar usuario y contraseña.")
            return

        if autenticar_usuario(usuario, contraseña):
            ventana.destroy()
            mostrar_pantalla_administrador(root, mostrar_pantalla_inicial)
        else:
            messagebox.showerror("Acceso Denegado", "Usuario o contraseña incorrectos.")

    # Botones
    tk.Button(
        ventana,
        text="Ingresar",
        font=("Arial", 12),
        command=intentar_acceso,
        bg="#4caf50",
        fg="white",
    ).pack(side="left", padx=20, pady=20)

    tk.Button(
        ventana,
        text="Cancelar",
        font=("Arial", 12),
        command=ventana.destroy,
        bg="#f44336",
        fg="white",
    ).pack(side="right", padx=20, pady=20)

    ventana.mainloop()



def iniciar_aplicacion():
    """
    Punto de entrada principal para la aplicación.
    """
    root = tk.Tk()
    root.title("Sistema de Marcación - NEXEL")
    root.geometry("1200x800")
    root.configure(bg=COLOR_FONDO)

    def mostrar_pantalla_inicial():
        for widget in root.winfo_children():
            widget.destroy()

        frame = tk.Frame(root, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True)

        titulo = tk.Label(frame, text="Bienvenido al Sistema de Marcación - NEXEL",
                          font=("Arial", 24, "bold"), bg=COLOR_FONDO, fg="#333")
        titulo.pack(pady=40)

        btn_usuario = tk.Button(frame, text="Acceder como Usuario", bg="#4caf50", fg="white",
                                font=("Arial", 14, "bold"),
                                command=lambda: acceder_como_usuario(root, mostrar_pantalla_inicial),
                                width=25, relief="flat")
        btn_usuario.pack(pady=15)

        btn_admin = tk.Button(frame, text="Acceder como Administrador", bg="#1976d2", fg="white",
                              font=("Arial", 14, "bold"),
                              command=lambda: validar_acceso_administrador(root, mostrar_pantalla_inicial),
                              width=25, relief="flat")
        btn_admin.pack(pady=15)

        footer = tk.Label(frame, text="© 2024 NEXEL - Sistema de Marcación",
                          font=("Arial", 10), bg=COLOR_FONDO, fg="#333")
        footer.pack(side="bottom", pady=20)

    mostrar_pantalla_inicial()
    root.mainloop()

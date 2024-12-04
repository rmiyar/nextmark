import tkinter as tk
from tkinter import messagebox
import os
from config import COLOR_FONDO
from user_screen import mostrar_pantalla_usuario
from admin_screen import mostrar_pantalla_administrador
from db import registrar_usuario, es_primera_vez_usuario, autenticar_administrador


def solicitar_datos_usuario(user_windows, continuar_callback):
    """
    Solicita el nombre y apellido del usuario al iniciar el programa por primera vez.
    """
    def confirmar_datos():
        nombre = entry_nombre.get().strip()
        apellido = entry_apellido.get().strip()

        if not nombre.isalpha():
            messagebox.showwarning("Advertencia", "El nombre debe ser solo letras.")
            return
        if not apellido.isalpha():
            messagebox.showwarning("Advertencia", "El apellido debe ser solo letras.")
            return

        # Registrar al usuario
        if registrar_usuario(nombre, apellido, user_windows):
            messagebox.showinfo("Bienvenido", f"¡Hola {nombre} {apellido}, bienvenido al sistema!")
            ventana.destroy()
            continuar_callback()  # Llama al callback para continuar con la aplicación
        else:
            messagebox.showerror("Error", f"El usuario {nombre} {apellido} no pudo ser registrado.")

    def cancelar():
        ventana.destroy()

    # Crear ventana emergente
    ventana = tk.Tk()  # Crear la ventana como principal para evitar la ventana vacía
    ventana.title("Configuración Inicial")
    ventana.geometry("400x250")
    ventana.configure(bg=COLOR_FONDO)

    tk.Label(ventana, text="Ingrese su nombre y apellido:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10)

    tk.Label(ventana, text="Nombre:", font=("Arial", 10), bg=COLOR_FONDO).pack(anchor="w", padx=20)
    entry_nombre = tk.Entry(ventana, font=("Arial", 12))
    entry_nombre.pack(padx=20, pady=5, fill="x")
    entry_nombre.focus()

    tk.Label(ventana, text="Apellido:", font=("Arial", 10), bg=COLOR_FONDO).pack(anchor="w", padx=20)
    entry_apellido = tk.Entry(ventana, font=("Arial", 12))
    entry_apellido.pack(padx=20, pady=5, fill="x")

    botones_frame = tk.Frame(ventana, bg=COLOR_FONDO)
    botones_frame.pack(pady=10)

    tk.Button(botones_frame, text="OK", font=("Arial", 12), command=confirmar_datos, bg="#4caf50", fg="white").pack(side="left", padx=10)
    tk.Button(botones_frame, text="Cancelar", font=("Arial", 12), command=cancelar, bg="#f44336", fg="white").pack(side="right", padx=10)

    ventana.mainloop()


def validar_acceso_administrador(root, mostrar_pantalla_inicial):
    """
    Valida el acceso del administrador verificando usuario y contraseña en la base de datos.
    """

    def intentar_acceso():
        """
        Intenta autenticar al usuario administrador.
        """
        usuario = entry_usuario.get().strip()
        contraseña = entry_contraseña.get().strip()
        user_windows = os.getlogin()  # Obtener el usuario de Windows actual

        if not usuario or not contraseña:
            messagebox.showwarning("Advertencia", "Debe ingresar usuario y contraseña.")
            return


        if autenticar_administrador(usuario, contraseña):
            ventana.destroy()
            mostrar_pantalla_administrador(root, mostrar_pantalla_inicial)
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales inválidas o no tiene permisos de administrador.")

    # Crear ventana emergente para solicitar credenciales
    ventana = tk.Toplevel(root)
    ventana.title("Acceso Administrador")
    ventana.geometry("400x250")
    ventana.configure(bg=COLOR_FONDO)
    ventana.grab_set()

    tk.Label(ventana, text="Usuario:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10, anchor="w", padx=20)
    entry_usuario = tk.Entry(ventana, font=("Arial", 12))
    entry_usuario.pack(padx=20, pady=5, fill="x")


    tk.Label(ventana, text="Contraseña:", font=("Arial", 12), bg=COLOR_FONDO).pack(pady=10, anchor="w", padx=20)
    entry_contraseña = tk.Entry(ventana, font=("Arial", 12), show="*")
    entry_contraseña.pack(padx=20, pady=5, fill="x")

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
    user_windows = os.getlogin()  # Obtiene el usuario actual de Windows

    # Verifica si es la primera vez
    if es_primera_vez_usuario(user_windows):
        solicitar_datos_usuario(user_windows, lambda: iniciar_ventana_principal())  # Llama a la función de inicio tras registro
    else:
        iniciar_ventana_principal()


def iniciar_ventana_principal():
    """
    Inicia la ventana principal de la aplicación.
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
                                command=lambda: mostrar_pantalla_usuario(root, mostrar_pantalla_inicial),
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


if __name__ == "__main__":
    iniciar_aplicacion()

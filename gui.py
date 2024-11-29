import tkinter as tk
from tkinter import simpledialog, messagebox
import os
from config import COLOR_FONDO
from user_screen import mostrar_pantalla_usuario
from admin_screen import mostrar_pantalla_administrador


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
            command=lambda: mostrar_pantalla_usuario(root, mostrar_pantalla_inicial),
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

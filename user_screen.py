import tkinter as tk
from tkinter import ttk, messagebox
from logic import marcar
from db import obtener_marcaciones_filtradas
from config import COLOR_FONDO, COLOR_HEADER, COLOR_TEXTO_HEADER, COLOR_BOTON_ENTRADA, COLOR_BOTON_SALIDA, COLOR_BOTON_VOLVER
import os
from datetime import datetime


def obtener_marcaciones_usuario_hoy(usuario_windows):
    """
    Obtiene las marcaciones del usuario actual desde la base de datos solo para el día actual.
    """
    try:
        # Obtener la fecha actual en formato YYYY-MM-DD
        fecha_actual = datetime.now().strftime("%Y-%m-%d")  # Formato compatible con la base de datos
        marcaciones = obtener_marcaciones_filtradas(usuario=usuario_windows, dia=fecha_actual)
        return marcaciones
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron obtener las marcaciones: {e}")
        return []


def actualizar_tabla(tabla, usuario_windows):
    """
    Actualiza la tabla con las marcaciones del usuario actual desde la base de datos, filtradas por el día actual.
    """
    try:
        # Limpiar la tabla antes de agregar nuevos datos
        for fila in tabla.get_children():
            tabla.delete(fila)

        # Obtener marcaciones del usuario actual para el día actual
        historial = obtener_marcaciones_usuario_hoy(usuario_windows)

        # Insertar los datos en la tabla
        for registro in historial:
            if len(registro) == 4:  # Asegurar que el registro tenga las columnas necesarias
                tabla.insert("", "end", values=registro)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la tabla: {e}")


def actualizar_hora(label_hora):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    label_hora.config(text=ahora)
    label_hora.after(1000, actualizar_hora, label_hora)


def mostrar_pantalla_usuario(root, volver_menu):
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, bg=COLOR_FONDO)
    frame.pack(fill="both", expand=True)

    usuario_windows = os.getlogin()

    header = tk.Frame(frame, bg=COLOR_HEADER)
    header.pack(fill="x", padx=10, pady=10)

    titulo = tk.Label(header, text=f"Usuario: {usuario_windows}", font=("Arial", 16, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    titulo.pack(side="left", padx=10)

    label_hora = tk.Label(header, text="", font=("Arial", 14), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    label_hora.pack(side="right", padx=10)

    actualizar_hora(label_hora)

    btn_entrada = tk.Button(
        frame,
        text="Registrar Marcación",
        bg=COLOR_BOTON_ENTRADA,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: [marcar(usuario_windows), actualizar_tabla(tabla, usuario_windows)],
        width=20,
        relief="flat",
    )
    btn_entrada.pack(pady=10)


    tabla_frame = tk.Frame(frame, bg=COLOR_FONDO)
    tabla_frame.pack(pady=20, fill="both", expand=True)

    columnas = ("Usuario", "Tipo de Marcación", "Fecha", "Hora")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=15)
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150, anchor="center")

    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scrollbar.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scrollbar.set)

    # Inicializar la tabla con datos del día actual
    actualizar_tabla(tabla, usuario_windows)

    btn_volver = tk.Button(
        frame,
        text="Volver al Menú Principal",
        bg=COLOR_BOTON_VOLVER,
        fg="white",
        font=("Arial", 14, "bold"),
        command=volver_menu,
        width=20,
        relief="flat",
    )
    btn_volver.pack(pady=10)

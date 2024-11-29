import tkinter as tk
from tkinter import ttk, messagebox
from logic import marcar
from config import COLOR_FONDO, COLOR_HEADER, COLOR_TEXTO_HEADER, COLOR_BOTON_ENTRADA, COLOR_BOTON_SALIDA, COLOR_BOTON_VOLVER
import os
from datetime import datetime


HISTORIAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historial_marcaciones.txt")


def cargar_historial():
    try:
        if not os.path.exists(HISTORIAL_PATH):
            return []
        with open(HISTORIAL_PATH, "r") as archivo:
            historial = []
            for line in archivo:
                datos = line.strip().split(",")
                if len(datos) == 4:
                    historial.append(datos)
            return historial
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el historial: {e}")
        return []


def actualizar_tabla(tabla):
    try:
        for fila in tabla.get_children():
            tabla.delete(fila)

        historial = cargar_historial()
        #print(f"Historial cargado: {historial}")  # Debug

        for registro in historial:
            if len(registro) == 4:
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

    usuario = os.getlogin()

    header = tk.Frame(frame, bg=COLOR_HEADER)
    header.pack(fill="x", padx=10, pady=10)

    titulo = tk.Label(header, text=f"Usuario: {usuario}", font=("Arial", 16, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    titulo.pack(side="left", padx=10)

    label_hora = tk.Label(header, text="", font=("Arial", 14), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    label_hora.pack(side="right", padx=10)

    actualizar_hora(label_hora)

    btn_entrada = tk.Button(
        frame,
        text="Marcar Entrada",
        bg=COLOR_BOTON_ENTRADA,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: [marcar(usuario, "entrada"), actualizar_tabla(tabla)],
        width=20,
        relief="flat",
    )
    btn_entrada.pack(pady=10)

    btn_salida = tk.Button(
        frame,
        text="Marcar Salida",
        bg=COLOR_BOTON_SALIDA,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: [marcar(usuario, "salida"), actualizar_tabla(tabla)],
        width=20,
        relief="flat",
    )
    btn_salida.pack(pady=10)

    tabla_frame = tk.Frame(frame, bg=COLOR_FONDO)
    tabla_frame.pack(pady=20, fill="both", expand=True)

    tabla = ttk.Treeview(tabla_frame, columns=("Usuario", "Tipo", "Fecha", "Hora"), show="headings", height=15)
    for col in ("Usuario", "Tipo", "Fecha", "Hora"):
        tabla.heading(col, text=col)
        tabla.column(col, width=150, anchor="center")

    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scrollbar.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scrollbar.set)

    actualizar_tabla(tabla)

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

import tkinter as tk
from tkinter import ttk, messagebox
import csv
from db import obtener_marcaciones_filtradas  # Nueva función en db.py
from config import COLOR_FONDO, COLOR_HEADER, COLOR_TEXTO_HEADER, COLOR_BOTON_VOLVER, COLOR_BOTON_DESCARGAR
from datetime import datetime
from db import conectar_bd

def actualizar_hora(label_hora):
    """
    Actualiza el reloj en tiempo real utilizando el método after().
    """
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    label_hora.config(text=ahora)
    label_hora.after(1000, actualizar_hora, label_hora)



def obtener_nombres_completos():
    """
    Consulta los nombres completos de los usuarios desde la tabla users.
    """
    connection = conectar_bd()
    if not connection:
        return []

    try:
        query = """
        SELECT CONCAT(nombre, ' ', apellido) AS nombre_completo
        FROM users
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            resultados = [row[0] for row in cursor.fetchall()]
        return resultados
    except Exception as e:
        print(f"Error al obtener nombres completos: {e}")
        return []
    finally:
        connection.close()    

def actualizar_tabla(tabla, filtros):
    """
    Limpia y actualiza la tabla con los datos filtrados de la base de datos.
    """
    try:
        for fila in tabla.get_children():
            tabla.delete(fila)

        marcaciones = obtener_marcaciones_filtradas(**filtros)
        for registro in marcaciones:
            if len(registro) == 4:
                tabla.insert("", "end", values=registro)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la tabla: {e}")

def descargar_marcaciones(filtros):
    """
    Descarga las marcaciones filtradas en un archivo CSV.
    """
    try:
        marcaciones = obtener_marcaciones_filtradas(**filtros)
        if not marcaciones:
            messagebox.showinfo("Información", "No hay datos para descargar.")
            return

        archivo = "marcaciones.csv"
        with open(archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre Completo", "Tipo de Marcación", "Fecha", "Hora"])  # Encabezados
            writer.writerows(marcaciones)

        messagebox.showinfo("Éxito", f"Marcaciones descargadas en {archivo}.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar las marcaciones: {e}")

def mostrar_pantalla_administrador(root, volver_menu):
    """
    Muestra la pantalla de administrador con filtros y la lista de marcaciones.
    """
    # Limpiar widgets actuales
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, bg=COLOR_FONDO)
    frame.pack(fill="both", expand=True)

    # Encabezado
    header = tk.Frame(frame, bg=COLOR_HEADER)
    header.pack(fill="x", padx=10, pady=10)

    titulo = tk.Label(header, text="Panel de Administrador", font=("Arial", 16, "bold"), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    titulo.pack(side="left", padx=10)

    label_hora = tk.Label(header, text="", font=("Arial", 14), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    label_hora.pack(side="right", padx=10)

    # Iniciar actualización de hora
    actualizar_hora(label_hora)

    # Filtros
    filtros_frame = tk.Frame(frame, bg=COLOR_FONDO)
    filtros_frame.pack(pady=10, padx=20, fill="x")

    tk.Label(filtros_frame, text="Nombre Completo:", bg=COLOR_FONDO, font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")

    # Crear el Combobox para nombres completos
    nombres_completos = obtener_nombres_completos()  # Obtener nombres desde la base de datos
    usuario_combobox = ttk.Combobox(filtros_frame, font=("Arial", 12), values=nombres_completos, state="readonly")
    usuario_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(filtros_frame, text="Tipo de Marcación:", bg=COLOR_FONDO, font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    tipo_combobox = ttk.Combobox(filtros_frame, font=("Arial", 12), values=["", "entrada", "salida"])
    tipo_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    tk.Label(filtros_frame, text="Día (DD-MM-YYYY):", bg=COLOR_FONDO, font=("Arial", 12)).grid(row=0, column=4, padx=5, pady=5, sticky="w")
    dia_entry = tk.Entry(filtros_frame, font=("Arial", 12))
    dia_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

    # Botón para aplicar filtros y actualizar la tabla
    btn_actualizar = tk.Button(
        filtros_frame,
        text="Aplicar Filtros",
        bg=COLOR_BOTON_DESCARGAR,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: actualizar_tabla(tabla, {
            "usuario": usuario_combobox.get().strip(),
            "tipo": tipo_combobox.get().strip(),
            "dia": dia_entry.get().strip(),
        }),
        width=25,
        relief="flat",
    )
    btn_actualizar.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

    # Tabla para mostrar las marcaciones
    tabla_frame = tk.Frame(frame, bg=COLOR_FONDO)
    tabla_frame.pack(pady=20, fill="both", expand=True)

    columnas = ("Nombre Completo", "Tipo de Marcación", "Fecha", "Hora")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=15)
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=150)

    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scrollbar.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scrollbar.set)

    # Botón para volver al menú principal
    btn_volver = tk.Button(
        frame,
        text="Volver al Menú Principal",
        bg=COLOR_BOTON_VOLVER,
        fg="white",
        font=("Arial", 14, "bold"),
        command=volver_menu,
        width=25,
        relief="flat",
    )
    btn_volver.pack(pady=10)

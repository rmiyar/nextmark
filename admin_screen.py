import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from db import obtener_marcaciones_admin, conectar_bd  # Funciones de base de datos
from config import (
    COLOR_FONDO,
    COLOR_HEADER,
    COLOR_TEXTO_HEADER,
    COLOR_BOTON_VOLVER,
    COLOR_BOTON_DESCARGAR,
)
from logic import calcular_horas_trabajadas  # Importar la lógica de cálculo de horas
from datetime import datetime, timedelta


def actualizar_hora(label_hora):
    """
    Actualiza el reloj en tiempo real utilizando el método after().
    """
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    label_hora.config(text=ahora)
    label_hora.after(1000, actualizar_hora, label_hora)


def configurar_estilo_notebook():
    """
    Configura el estilo del ttk.Notebook para agrandar las pestañas.
    """
    estilo = ttk.Style()
    estilo.configure(
        "TNotebook.Tab",
        padding=[20, 10],
        font=("Arial", 12, "bold"),
    )


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


def actualizar_tabla_admin(tabla, filtros):
    """
    Limpia y actualiza la tabla con los datos filtrados desde la función para administradores.
    """
    try:
        for fila in tabla.get_children():
            tabla.delete(fila)

        desde = filtros.get("desde")
        hasta = filtros.get("hasta")
        if desde and hasta:
            try:
                datetime.strptime(desde, "%d-%m-%Y")
                datetime.strptime(hasta, "%d-%m-%Y")
            except ValueError:
                messagebox.showerror("Error", "Las fechas deben estar en formato DD-MM-YYYY.")
                return

        marcaciones = obtener_marcaciones_admin(
            usuario=filtros.get("usuario"),
            tipo=filtros.get("tipo"),
            desde=desde,
            hasta=hasta,
        )
        for registro in marcaciones:
            if len(registro) == 4:
                tabla.insert("", "end", values=registro)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar la tabla: {e}")


def generar_csv_marcaciones(tabla):
    """
    Genera un archivo CSV con las marcaciones actualmente visibles en la tabla.
    """
    try:
        filas = [tabla.item(fila)["values"] for fila in tabla.get_children()]
        if not filas:
            messagebox.showinfo("Información", "No hay marcaciones para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            title="Guardar marcaciones como CSV",
        )
        if not archivo:
            return

        with open(archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nombre Completo", "Tipo de Marcación", "Fecha", "Hora"])
            writer.writerows(filas)

        messagebox.showinfo("Éxito", f"Marcaciones guardadas en: {archivo}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo CSV: {e}")


def calcular_horas_tab(usuario, desde, hasta, label_resultado):
    """
    Calcula las horas trabajadas desde la interfaz gráfica y envía las fechas correctamente formateadas a la base de datos.
    """
    try:
        # Validar que los campos no estén vacíos
        if not usuario or not desde or not hasta:
            messagebox.showerror("Error", "Todos los campos deben estar completos.")
            return

        # Convertir fechas de DD-MM-YYYY a YYYY-MM-DD para la base de datos
        try:
            desde_db = datetime.strptime(desde, "%d-%m-%Y").strftime("%Y-%m-%d")
            hasta_db = datetime.strptime(hasta, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Las fechas deben estar en formato DD-MM-YYYY.")
            return

        # Imprimir los valores para depuración
        print(f"Usuario seleccionado: {usuario}")
        print(f"Fecha desde (convertida): {desde_db}")
        print(f"Fecha hasta (convertida): {hasta_db}")

        # Obtener marcaciones desde la base de datos
        marcaciones = obtener_marcaciones_admin(usuario=usuario, desde=desde_db, hasta=hasta_db)

        # Imprimir las marcaciones obtenidas
        print(f"Marcaciones obtenidas: {marcaciones}")

        if not marcaciones:
            messagebox.showinfo("Información", "No se encontraron marcaciones para el usuario en el rango dado.")
            return

        # Pasar las marcaciones a calcular_horas_trabajadas
        horas, minutos = calcular_horas_trabajadas(usuario, desde_db, hasta_db, marcaciones)

        # Mostrar el resultado en la interfaz
        label_resultado.config(
            text=f"Total de horas trabajadas: {horas} horas y {minutos} minutos."
        )
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo calcular las horas trabajadas: {e}")



def mostrar_pantalla_administrador(root, volver_menu):
    """
    Muestra la pantalla de administrador con filtros y la lista de marcaciones.
    """
    for widget in root.winfo_children():
        widget.destroy()

    frame = tk.Frame(root, bg=COLOR_FONDO)
    frame.pack(fill="both", expand=True)

    header = tk.Frame(frame, bg=COLOR_HEADER)
    header.pack(fill="x", padx=10, pady=10)

    titulo = tk.Label(
        header,
        text="Panel de Administrador",
        font=("Arial", 16, "bold"),
        bg=COLOR_HEADER,
        fg=COLOR_TEXTO_HEADER,
    )
    titulo.pack(side="left", padx=10)

    label_hora = tk.Label(header, text="", font=("Arial", 14), bg=COLOR_HEADER, fg=COLOR_TEXTO_HEADER)
    label_hora.pack(side="right", padx=10)

    actualizar_hora(label_hora)
    configurar_estilo_notebook()

    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    tab1 = tk.Frame(notebook, bg=COLOR_FONDO)
    notebook.add(tab1, text="Gestión de Marcaciones")

    tab2 = tk.Frame(notebook, bg=COLOR_FONDO)
    notebook.add(tab2, text="Cálculo de Horas")

    mostrar_tab1(tab1, volver_menu)
    mostrar_tab2(tab2)


def mostrar_tab1(tab, volver_menu):
    """
    Contenido de la Tab 1: Funcionalidades existentes.
    """
    filtros_frame = tk.Frame(tab, bg=COLOR_FONDO)
    filtros_frame.pack(pady=10, padx=20, fill="x")

    tk.Label(filtros_frame, text="Nombre Completo:", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )

    nombres_completos = obtener_nombres_completos()
    usuario_combobox = ttk.Combobox(filtros_frame, font=("Arial", 12), values=nombres_completos, state="readonly")
    usuario_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(filtros_frame, text="Tipo de Marcación:", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=0, column=2, padx=5, pady=5, sticky="w"
    )
    tipo_combobox = ttk.Combobox(filtros_frame, font=("Arial", 12), values=["", "entrada", "salida"])
    tipo_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

    tk.Label(filtros_frame, text="Desde (DD-MM-YYYY):", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    desde_entry = tk.Entry(filtros_frame, font=("Arial", 12))
    desde_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(filtros_frame, text="Hasta (DD-MM-YYYY):", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )
    hasta_entry = tk.Entry(filtros_frame, font=("Arial", 12))
    hasta_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    tabla_frame = tk.Frame(tab, bg=COLOR_FONDO)
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

    btn_actualizar = tk.Button(
        filtros_frame,
        text="Aplicar Filtros",
        bg=COLOR_BOTON_DESCARGAR,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: actualizar_tabla_admin(
            tabla,
            {
                "usuario": usuario_combobox.get().strip(),
                "tipo": tipo_combobox.get().strip(),
                "desde": desde_entry.get().strip(),
                "hasta": hasta_entry.get().strip(),
            },
        ),
        width=25,
        relief="flat",
    )
    btn_actualizar.grid(row=2, column=0, columnspan=4, pady=10, sticky="w")

    btn_generar_csv = tk.Button(
        tab,
        text="Exportar Datos Visibles a CSV",
        bg=COLOR_BOTON_DESCARGAR,
        fg="white",
        font=("Arial", 14, "bold"),
        command=lambda: generar_csv_marcaciones(tabla),
        width=25,
        relief="flat",
    )
    btn_generar_csv.pack(pady=10)

    btn_volver = tk.Button(
        tab,
        text="Volver al Menú Principal",
        bg=COLOR_BOTON_VOLVER,
        fg="white",
        font=("Arial", 14, "bold"),
        command=volver_menu,
        width=25,
        relief="flat",
    )
    btn_volver.pack(pady=10)


def mostrar_tab2(tab):
    """
    Contenido de la Tab 2: Cálculo de Horas.
    """
    frame = tk.Frame(tab, bg=COLOR_FONDO)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Filtros
    tk.Label(frame, text="Nombre Completo:", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=0, column=0, padx=5, pady=5, sticky="w"
    )
    nombres_completos = obtener_nombres_completos()
    usuario_combobox = ttk.Combobox(frame, font=("Arial", 12), values=["Todos"] + nombres_completos, state="readonly")
    usuario_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="Desde (DD-MM-YYYY):", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=1, column=0, padx=5, pady=5, sticky="w"
    )
    desde_entry = tk.Entry(frame, font=("Arial", 12))
    desde_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(frame, text="Hasta (DD-MM-YYYY):", bg=COLOR_FONDO, font=("Arial", 12)).grid(
        row=1, column=2, padx=5, pady=5, sticky="w"
    )
    hasta_entry = tk.Entry(frame, font=("Arial", 12))
    hasta_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    # Tabla para mostrar los resultados
    tabla_frame = tk.Frame(frame, bg=COLOR_FONDO)
    tabla_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=20, sticky="nsew")

    columnas = ("Usuario", "Fecha Desde", "Fecha Hasta", "Horas", "Minutos")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=10)
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=150)

    tabla.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scrollbar.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scrollbar.set)

    # Configurar el peso de las filas y columnas
    frame.grid_rowconfigure(2, weight=1)  # Hacer que la fila 2 (tabla) sea expandible
    frame.grid_columnconfigure(1, weight=1)  # Hacer que las columnas se expandan

    # Función para calcular y llenar la tabla
    def calcular_horas_para_tabla():
        tabla.delete(*tabla.get_children())  # Limpiar la tabla

        usuario_seleccionado = usuario_combobox.get()
        desde = desde_entry.get()
        hasta = hasta_entry.get()

        if not desde or not hasta:
            messagebox.showerror("Error", "Debes completar las fechas.")
            return

        try:
            desde_db = datetime.strptime(desde, "%d-%m-%Y").strftime("%Y-%m-%d")
            hasta_db = datetime.strptime(hasta, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Las fechas deben estar en formato DD-MM-YYYY.")
            return

        if usuario_seleccionado == "Todos":
            usuarios = obtener_nombres_completos()
        else:
            usuarios = [usuario_seleccionado]

        for usuario in usuarios:
            marcaciones = obtener_marcaciones_admin(usuario=usuario, desde=desde_db, hasta=hasta_db)

            if not marcaciones:
                continue

            horas, minutos = calcular_horas_trabajadas(usuario, desde_db, hasta_db, marcaciones)
            tabla.insert("", "end", values=(usuario, desde, hasta, horas, minutos))

    # Botón para calcular y mostrar los resultados
    btn_calcular = tk.Button(
        frame,
        text="Calcular Horas",
        bg=COLOR_BOTON_DESCARGAR,
        fg="white",
        font=("Arial", 14, "bold"),
        command=calcular_horas_para_tabla,
        width=25,
        relief="flat",
    )
    btn_calcular.grid(row=3, column=0, columnspan=2, pady=10)

    # Botón para exportar a CSV
    def exportar_csv():
        filas = [tabla.item(fila)["values"] for fila in tabla.get_children()]
        if not filas:
            messagebox.showinfo("Información", "No hay datos para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            title="Guardar como CSV",
        )
        if not archivo:
            return

        with open(archivo, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Usuario", "Fecha Desde", "Fecha Hasta", "Horas", "Minutos"])  # Encabezados
            writer.writerows(filas)

        messagebox.showinfo("Éxito", f"Datos exportados a {archivo}.")

    btn_exportar = tk.Button(
        frame,
        text="Exportar a CSV",
        bg=COLOR_BOTON_VOLVER,
        fg="white",
        font=("Arial", 14, "bold"),
        command=exportar_csv,
        width=25,
        relief="flat",
    )
    btn_exportar.grid(row=3, column=2, columnspan=2, pady=10)


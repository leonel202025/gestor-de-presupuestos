import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime
from tkinter import PhotoImage
import os
import sys
import json

def resource_path(relative_path):
    """ Devuelve la ruta absoluta del archivo de recursos,
    sea en el script o en el ejecutable generado por PyInstaller. """
    try:
        # Si estamos en un ejecutable, obtendremos el path de la carpeta temporal
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

class PresupuestoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Presupuestos Eléctricos")
        self.centrar_ventana(self.root, 800, 600)

        # Inicializar presupuestos y historial de pagos
        self.presupuestos = []
        self.historial_pagos = {}

        # Cargar los datos guardados
        self.cargar_datos()

        # Cargar iconos usando la función resource_path para obtener la ruta correcta
        self.icono_agregar = PhotoImage(file=resource_path("icono_agregar.png"))
        self.icono_ver = PhotoImage(file=resource_path("icono_ver.png"))
        self.icono_volver = PhotoImage(file=resource_path("icono_volver.png"))

        # Página de inicio (Menú principal)
        self.menu_frame = ttk.Frame(root, padding="20")
        self.menu_frame.pack(fill=tk.BOTH, expand=True)

        # Crear un sub-frame para centrar el contenido vertical y horizontalmente
        contenido_frame = ttk.Frame(self.menu_frame)
        contenido_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Título del menú principal
        titulo_menu = ttk.Label(contenido_frame, text="Gestor de Presupuestos Eléctricos", font=("Arial", 20))
        titulo_menu.pack(pady=20)

        # Botones del menú principal
        boton_agregar = ttk.Button(contenido_frame, text="Agregar Nuevo Presupuesto", image=self.icono_agregar, compound="left", command=self.mostrar_agregar_presupuesto, width=30)
        boton_agregar.pack(pady=10)

        boton_ver_presupuestos = ttk.Button(contenido_frame, text="Ver Todos los Presupuestos", image=self.icono_ver, compound="left", command=self.mostrar_presupuestos, width=30)
        boton_ver_presupuestos.pack(pady=10)

        # Página de agregar presupuesto
        self.main_frame = ttk.Frame(root, padding="20")

        # Ajustar tamaño de fuente
        label_font = ("Arial", 16)
        entry_font = ("Arial", 14)

        # Estilizar y organizar los elementos
        contenido_agregar_frame = ttk.Frame(self.main_frame, padding="20", relief="solid")
        contenido_agregar_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Label(contenido_agregar_frame, text="Agregar Nuevo Presupuesto", font=("Arial", 20, "bold"), anchor="center").pack(pady=10)

        ttk.Label(contenido_agregar_frame, text="Nombre y Apellido del Cliente:", font=label_font).pack(pady=5, anchor="w")
        self.entry_cliente = ttk.Entry(contenido_agregar_frame, font=entry_font, width=30)
        self.entry_cliente.pack(pady=5)

        ttk.Label(contenido_agregar_frame, text="Domicilio del Cliente:", font=label_font).pack(pady=5, anchor="w")
        self.entry_domicilio = ttk.Entry(contenido_agregar_frame, font=entry_font, width=30)
        self.entry_domicilio.pack(pady=5)

        ttk.Label(contenido_agregar_frame, text="Total del Presupuesto:", font=label_font).pack(pady=5, anchor="w")
        self.entry_presupuesto = ttk.Entry(contenido_agregar_frame, font=entry_font, width=30)

        if not self.entry_presupuesto.get():
            self.entry_presupuesto.insert(0, "$")

        self.entry_presupuesto.pack(pady=5)

        # Vincular eventos de teclado
        self.entry_cliente.bind("<Return>", lambda event: self.entry_domicilio.focus())
        self.entry_domicilio.bind("<Return>", lambda event: self.entry_presupuesto.focus())
        self.entry_presupuesto.bind("<Return>", lambda event: self.agregar_cliente_si_completo())

        # Agregar separador decorativo
        ttk.Separator(contenido_agregar_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Botones de acción
        self.boton_agregar_cliente = ttk.Button(contenido_agregar_frame, text="Agregar Presupuesto", command=self.agregar_cliente, width=25)
        self.boton_agregar_cliente.pack(pady=10)

        botones_acciones = ttk.Frame(contenido_agregar_frame)
        botones_acciones.pack(pady=10)

        ttk.Button(botones_acciones, text="Ver Todos los Presupuestos", image=self.icono_ver, compound="left", command=self.mostrar_presupuestos, width=25).grid(row=0, column=0, padx=5)

        ttk.Button(botones_acciones, text="Volver al Menú Principal", image=self.icono_volver, compound="left", command=self.mostrar_menu, width=25).grid(row=0, column=1, padx=5)

        # Página de tabla de presupuestos
        self.tabla_frame = ttk.Frame(root, padding="20")
        self.tabla = ttk.Treeview(self.tabla_frame, columns=("Cliente", "Domicilio", "Presupuesto", "Deuda"), show="headings", height=10)
        self.tabla.heading("Cliente", text="Cliente", anchor="center")
        self.tabla.heading("Domicilio", text="Domicilio", anchor="center")
        self.tabla.heading("Presupuesto", text="Presupuesto", anchor="center")
        self.tabla.heading("Deuda", text="Deuda", anchor="center")

        self.tabla.column("Cliente", anchor="center", width=200)
        self.tabla.column("Domicilio", anchor="center", width=200)
        self.tabla.column("Presupuesto", anchor="center", width=150)
        self.tabla.column("Deuda", anchor="center", width=150)

        self.tabla.pack(fill=tk.BOTH, expand=True)

        self.tabla.bind("<<TreeviewSelect>>", self.habilitar_botones)

        botones_frame = ttk.Frame(self.tabla_frame)
        botones_frame.pack(pady=20)

        self.boton_registrar_pago = ttk.Button(botones_frame, text="Registrar Pago", state=tk.DISABLED, command=self.registrar_pago, width=20)
        self.boton_registrar_pago.grid(row=0, column=0, padx=10, pady=5)

        self.boton_historial_pagos = ttk.Button(botones_frame, text="Historial de Pagos", state=tk.DISABLED, command=self.ver_historial_pagos, width=20)
        self.boton_historial_pagos.grid(row=0, column=1, padx=10, pady=5)

        self.boton_eliminar_cliente = ttk.Button(botones_frame, text="Eliminar Cliente", state=tk.DISABLED, command=self.eliminar_cliente, width=20)
        self.boton_eliminar_cliente.grid(row=0, column=2, padx=10, pady=5)

        ttk.Button(self.tabla_frame, text="Volver al Menú Principal", image=self.icono_volver, compound="left", command=self.mostrar_menu, width=25).pack(pady=10)

        self.entry_cliente.focus()

    def centrar_ventana(self, ventana, ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        posicion_x = (pantalla_ancho // 2) - (ancho // 2)
        posicion_y = (pantalla_alto // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{posicion_x}+{posicion_y}")

    def agregar_cliente_si_completo(self):
        if self.entry_cliente.get().strip() and self.entry_domicilio.get().strip() and self.entry_presupuesto.get().strip():
            self.agregar_cliente()

    def guardar_datos(self):
        try:
            with open("presupuestos.json", "w") as archivo:
                datos = {
                    "presupuestos": self.presupuestos,
                    "historial_pagos": self.historial_pagos
                }
                json.dump(datos, archivo, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar los datos: {str(e)}")

    def cargar_datos(self):
        try:
            if os.path.exists("presupuestos.json"):
                with open("presupuestos.json", "r") as archivo:
                    datos = json.load(archivo)
                    self.presupuestos = datos.get("presupuestos", [])
                    self.historial_pagos = datos.get("historial_pagos", {})
            else:
                self.presupuestos = []
                self.historial_pagos = {}
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos: {str(e)}")

    def agregar_cliente(self):
        cliente = self.entry_cliente.get().strip()
        domicilio = self.entry_domicilio.get().strip()
        presupuesto_texto = self.entry_presupuesto.get().strip()

        if not cliente or not domicilio or not presupuesto_texto:
            messagebox.showerror("Error", "Debe ingresar un nombre, domicilio y un presupuesto.")
            return

        try:
            presupuesto = float(re.sub(r"[^\d]", "", presupuesto_texto))
        except ValueError:
            messagebox.showerror("Error", "El presupuesto debe ser un número válido.")
            return

        if presupuesto <= 0:
            messagebox.showerror("Error", "El presupuesto debe ser mayor a 0.")
            return

        cliente = cliente.title()

        nuevo_cliente = {
            "Cliente": cliente,
            "Domicilio": domicilio,
            "Presupuesto": presupuesto,
            "Deuda": presupuesto
        }
        self.presupuestos.append(nuevo_cliente)
        self.historial_pagos[cliente] = []

        self.entry_cliente.delete(0, tk.END)
        self.entry_domicilio.delete(0, tk.END)
        self.entry_presupuesto.delete(0, tk.END)
        self.entry_presupuesto.insert(0, "$")
        messagebox.showinfo("Éxito", "Cliente agregado exitosamente.")
        
        # Guardar los datos después de agregar el cliente
        self.guardar_datos()

        self.entry_cliente.focus()

    def mostrar_agregar_presupuesto(self):
        self.menu_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.entry_cliente.focus()  # Establecer el foco en el primer input

    def mostrar_presupuestos(self):
        if not self.presupuestos:
            messagebox.showinfo("Información", "No hay presupuestos registrados hasta el momento.")
            return

        self.menu_frame.pack_forget()
        self.main_frame.pack_forget()
        self.tabla_frame.pack(fill=tk.BOTH, expand=True)
        self.cargar_datos_tabla()

    def cargar_datos_tabla(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        for presupuesto in self.presupuestos:
            presupuesto_format = f"${int(presupuesto['Presupuesto']):,}".replace(",", ".")
            deuda_format = f"${int(presupuesto['Deuda']):,}".replace(",", ".")
            self.tabla.insert("", "end", values=(presupuesto["Cliente"], presupuesto["Domicilio"], presupuesto_format, deuda_format))

    def habilitar_botones(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            cliente = self.tabla.item(seleccion[0])["values"][0]
            deuda_str = self.tabla.item(seleccion[0])["values"][3]

            deuda = float(deuda_str.replace("$", "").replace(".", "").replace(",", ""))

            self.boton_registrar_pago.config(state=tk.NORMAL)

            if self.historial_pagos.get(cliente):
                self.boton_historial_pagos.config(state=tk.NORMAL)
            else:
                self.boton_historial_pagos.config(state=tk.DISABLED)

            if deuda == 0:
                self.boton_eliminar_cliente.config(state=tk.NORMAL)
            else:
                self.boton_eliminar_cliente.config(state=tk.DISABLED)

        else:
            self.boton_registrar_pago.config(state=tk.DISABLED)
            self.boton_historial_pagos.config(state=tk.DISABLED)
            self.boton_eliminar_cliente.config(state=tk.DISABLED)

    def registrar_pago(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        cliente = self.tabla.item(seleccion[0])["values"][0]

        def guardar_pago():
            try:
                # Obtener el monto del pago
                nuevo_pago_texto = entry_pago.get().strip()
                nuevo_pago = float(re.sub(r"[^\d]", "", nuevo_pago_texto))

                if nuevo_pago <= 0:
                    raise ValueError("El pago debe ser positivo.")

                # Obtener la fecha manual
                fecha_manual = entry_fecha.get().strip()
                if not re.match(r"^\d{2}/\d{2}/\d{4}$", fecha_manual):
                    raise ValueError("La fecha debe tener el formato DD/MM/AAAA.")

                # Actualizar la deuda del cliente
                for presupuesto in self.presupuestos:
                    if presupuesto["Cliente"] == cliente:
                        presupuesto["Deuda"] -= nuevo_pago
                        if presupuesto["Deuda"] < 0:
                            presupuesto["Deuda"] = 0.0
                        break

                # Verificar si el cliente tiene historial de pagos, si no, lo crea
                if cliente not in self.historial_pagos:
                    self.historial_pagos[cliente] = []

                # Agregar el nuevo pago al historial del cliente
                self.historial_pagos[cliente].append({
                    "monto": nuevo_pago,
                    "fecha": fecha_manual  # Usar la fecha manual ingresada
                })

                # Guardar los datos en el archivo JSON
                self.guardar_datos()

                # Actualizar la tabla y cerrar la ventana de pago
                self.cargar_datos_tabla()
                self.habilitar_botones(None)  # Actualizar botones después de registrar el pago
                ventana_pago.destroy()
                messagebox.showinfo("Éxito", "Pago registrado exitosamente.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Error inesperado: {e}")

        # Crear la ventana de pago
        ventana_pago = tk.Toplevel(self.root)
        ventana_pago.title("Registrar Pago")
        self.centrar_ventana(ventana_pago, 350, 230)  # Ajustar el tamaño de la ventana

        # Campo para el monto del pago
        ttk.Label(ventana_pago, text="Monto del Pago:", font=("Arial", 14)).pack(pady=(20, 5))
        entry_pago = ttk.Entry(ventana_pago, font=("Arial", 14), width=20)
        entry_pago.pack(pady=5)
        entry_pago.insert(0, "$")  # Mostrar el signo "$" al principio del campo

        # Campo para la fecha manual
        ttk.Label(ventana_pago, text="Fecha del Pago:", font=("Arial", 14)).pack(pady=(10, 5))
        entry_fecha = ttk.Entry(ventana_pago, font=("Arial", 14), width=20)
        entry_fecha.pack(pady=5)

        # Botón para registrar el pago
        ttk.Button(ventana_pago, text="Registrar Pago", command=guardar_pago, width=20).pack(pady=10)

        # Asociar la tecla Enter al botón de guardar pago
        entry_pago.bind("<Return>", lambda event: guardar_pago())
        entry_fecha.bind("<Return>", lambda event: guardar_pago())

        entry_pago.focus()

    def ver_historial_pagos(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        cliente = self.tabla.item(seleccion[0])["values"][0]

        historial = self.historial_pagos.get(cliente, [])
        if not historial:
            messagebox.showinfo("Historial de Pagos", "Este cliente no tiene pagos registrados.")
            return

        ventana_historial = tk.Toplevel(self.root)
        ventana_historial.title(f"Historial de Pagos de {cliente}")
        self.centrar_ventana(ventana_historial, 500, 400)

        tabla_historial = ttk.Treeview(ventana_historial, columns=("Pago", "Fecha"), show="headings", height=10)
        tabla_historial.heading("Pago", text="Pago", anchor="center")
        tabla_historial.heading("Fecha", text="Fecha", anchor="center")
        
        tabla_historial.column("Pago", anchor="center", width=150)
        tabla_historial.column("Fecha", anchor="center", width=200)
        tabla_historial.pack(fill=tk.BOTH, expand=True)

        for pago in historial:
            tabla_historial.insert("", "end", values=(f"${int(pago['monto']):,}".replace(",", "."), pago['fecha']))

    def eliminar_cliente(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return

        cliente = self.tabla.item(seleccion[0])["values"][0]
    
        def confirmar_eliminacion():
            # Eliminar al cliente de la lista de presupuestos y del historial de pagos
            self.presupuestos = [presupuesto for presupuesto in self.presupuestos if presupuesto["Cliente"] != cliente]
            del self.historial_pagos[cliente]
        
            # Actualizar la tabla de datos
            self.cargar_datos_tabla()
            self.habilitar_botones(None)  # Actualizar los botones después de eliminar el cliente
        
            # Guardar los datos después de eliminar el cliente
            self.guardar_datos()

            ventana_eliminacion.destroy()
            messagebox.showinfo("Éxito", "Cliente eliminado exitosamente.")

        ventana_eliminacion = tk.Toplevel(self.root)
        ventana_eliminacion.title("Eliminar Cliente")
        self.centrar_ventana(ventana_eliminacion, 400, 200)

        ttk.Label(ventana_eliminacion, text=f"Se eliminará a {cliente}", font=("Arial", 16)).pack(pady=20)

        ttk.Button(ventana_eliminacion, text="Eliminar", command=confirmar_eliminacion, width=20).pack(pady=10)
        ttk.Button(ventana_eliminacion, text="Cancelar", command=ventana_eliminacion.destroy, width=20).pack(pady=10)

    def mostrar_menu(self):
        self.tabla_frame.pack_forget()
        self.main_frame.pack_forget()
        self.menu_frame.pack(fill=tk.BOTH, expand=True)  # Volver al menú principal

# Configuración inicial
root = tk.Tk()
app = PresupuestoApp(root)
root.mainloop()
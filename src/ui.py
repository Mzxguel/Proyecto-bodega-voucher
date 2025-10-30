import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from .db_manager import DBManager
from .ventas_mananger import VentasManager
from .printer import generar_voucher_pdf
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import Tk, Label, PhotoImage
import os

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Bodega SILMIG - Local')
        self.root.geometry('900x600')

        self.db = DBManager()
        try:
            self.venta_mgr = VentasManager(self.db)
        except TypeError:
            self.venta_mgr = VentasManager()

        self.carrito = [] # lista de dicts: producto_id, nombre, cantidad, precio
        self.metodo_pago = "EFECTIVO"  # Método de pago por defecto

        self._crear_widgets()

    def _crear_widgets(self):
        # === Menú superior ===
        menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        menu_frame.pack(fill='x', pady=6)

        tk.Button(menu_frame, text='Modo: Agregar Producto', command=self.modo_agregar).pack(side='left', padx=6)
        tk.Button(menu_frame, text='Modo: Vender', command=self.modo_vender).pack(side='left', padx=6)
        tk.Button(menu_frame, text='Administrar Productos', command=self.abrir_admin).pack(side='left', padx=6)
        tk.Button(menu_frame, text='Ver Vouchers', command=self.abrir_vouchers).pack(side='left', padx=6)

        # === LOGO DE LA BODEGA EN ESQUINA SUPERIOR DERECHA ===
        try:
            # Obtener ruta absoluta del logo
            base_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(base_dir, "..", "assets", "imgSilmig.jpg")

            # Cargar y redimensionar imagen
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((80, 80))  # Ajusta el tamaño
            self.logo_photo = ImageTk.PhotoImage(logo_img)

            # Crear etiqueta y colocarla a la derecha del menú
            logo_label = tk.Label(menu_frame, image=self.logo_photo, bg="#f0f0f0")
            logo_label.pack(side='right', padx=10)
        except Exception as e:
            print(f"⚠️ No se pudo cargar el logo: {e}")

        # === Área central ===
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Por defecto: modo vender
        self.modo_vender()

    def limpiar_main(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    # ---------------- MODO AGREGAR ----------------
    def modo_agregar(self):
        self.limpiar_main()
        tk.Label(self.main_frame, text='Escanea el código para agregar el producto:').pack(pady=8)
        self.entry_agregar = tk.Entry(self.main_frame, font=('Arial', 14), width=30)
        self.entry_agregar.pack()
        self.entry_agregar.focus_set()
        self.entry_agregar.bind('<Return>', self._on_scan_agregar)

    def _on_scan_agregar(self, event):
        codigo = self.entry_agregar.get().strip()
        if not codigo:
            return
        # Abrir diálogo para pedir datos del producto
        nombre = simpledialog.askstring('Nombre', 'Nombre del producto:')
        if not nombre:
            messagebox.showwarning('Aviso', 'Nombre es obligatorio')
            return
        try:
            precio = float(simpledialog.askstring('Precio', 'Precio:'))
        except Exception:
            messagebox.showwarning('Aviso', 'Precio inválido')
            return
        try:
            stock = int(simpledialog.askstring('Stock', 'Stock inicial:'))
        except Exception:
            stock = 0

        ok = self.db.agregar_producto(codigo, nombre, precio, stock)
        if ok:
            messagebox.showinfo('Ok', 'Producto agregado correctamente')
        else:
            messagebox.showerror('Error', 'El código ya existe en la base de datos')
        self.entry_agregar.delete(0, 'end')

    # ---------------- MODO VENDER ----------------
    def modo_vender(self):
        self.limpiar_main()
        top = tk.Frame(self.main_frame)
        top.pack(fill='x', pady=6)

        tk.Label(top, text='Escanea el producto:').pack(side='left', padx=6)
        self.entry_vender = tk.Entry(top, font=('Arial', 14), width=30)
        self.entry_vender.pack(side='left')
        self.entry_vender.focus_set()
        self.entry_vender.bind('<Return>', self._on_scan_vender)

        # Tabla carrito
        cols = ('producto', 'cant', 'precio')
        self.tree = ttk.Treeview(self.main_frame, columns=cols, show='headings', height=12)
        self.tree.heading('producto', text='Producto')
        self.tree.heading('cant', text='Cant.')
        self.tree.heading('precio', text='Precio')
        self.tree.pack(pady=10, fill='x')

        bottom = tk.Frame(self.main_frame)
        bottom.pack(fill='x', pady=6)
        
        # Frame para método de pago
        pago_frame = tk.Frame(bottom)
        pago_frame.pack(side='left', padx=10)
        
        tk.Label(pago_frame, text='Método de Pago:', font=('Arial', 10)).pack(side='left')
        
        # Combobox para método de pago
        self.metodo_pago_var = tk.StringVar(value="EFECTIVO")
        metodos_pago = ["EFECTIVO", "YAPE", "PLIN", "CRÉDITO"]
        self.combo_pago = ttk.Combobox(pago_frame, 
                                     textvariable=self.metodo_pago_var,
                                     values=metodos_pago,
                                     state="readonly",
                                     width=12)
        self.combo_pago.pack(side='left', padx=5)
        self.combo_pago.bind('<<ComboboxSelected>>', self._cambiar_metodo_pago)

        self.label_total = tk.Label(bottom, text='TOTAL: S/ 0.00', font=('Arial', 14, 'bold'))
        self.label_total.pack(side='left', padx=10)

        tk.Button(bottom, text='Imprimir voucher', command=self.finalizar_venta, bg='#4CAF50', fg='white').pack(side='right', padx=6)
        tk.Button(bottom, text='Cancelar', command=self.cancelar_venta, bg='#f44336', fg='white').pack(side='right')

    def _cambiar_metodo_pago(self, event=None):
        """Actualiza el método de pago seleccionado"""
        self.metodo_pago = self.metodo_pago_var.get()

    def _on_scan_vender(self, event):
        codigo = self.entry_vender.get().strip()
        if not codigo:
            return
        row = self.db.obtener_producto_por_codigo(codigo)
        if not row:
            messagebox.showerror('No encontrado', 'Producto no existe. Cambia a Modo Agregar para registrarlo')
            self.entry_vender.delete(0, 'end')
            return
        pid, codigo, nombre, precio, stock = row
        # Ver si ya está en carrito -> aumentar cantidad
        for item in self.carrito:
            if item['producto_id'] == pid:
                # verificar stock: no permitir exceder el stock en la BD
                cantidad_actual = item['cantidad']
                if cantidad_actual >= stock:
                    messagebox.showwarning('Sin stock', f"No hay más stock disponible para '{nombre}'. Stock: {stock}")
                    self.entry_vender.delete(0, 'end')
                    return
                item['cantidad'] += 1
                self._refresh_carrito()
                self.entry_vender.delete(0, 'end')
                return
        # si no está, agregar
        # antes de agregar, verificar que exista stock (al menos 1)
        if stock <= 0:
            messagebox.showwarning('Sin stock', f"El producto '{nombre}' no tiene stock disponible.")
            self.entry_vender.delete(0, 'end')
            return

        self.carrito.append({'producto_id': pid, 'nombre': nombre, 'cantidad': 1, 'precio': precio})
        self._refresh_carrito()
        self.entry_vender.delete(0, 'end')

    def _refresh_carrito(self):
        # limpiar tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        total = 0.0
        for item in self.carrito:
            subtotal = item['cantidad'] * item['precio']
            total += subtotal
            self.tree.insert('', 'end', values=(item['nombre'], item['cantidad'], f'S/ {subtotal:.2f}'))
        self.label_total.config(text=f'TOTAL: S/ {total:.2f}')

    def cancelar_venta(self):
        self.carrito = []
        self._refresh_carrito()

    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "No hay productos en el carrito.")
            return

        # Some VentasManager implementations return a dict, others return (venta_id, total)
        res = self.venta_mgr.procesar_venta(self.carrito)
        # normalize response
        if isinstance(res, dict):
            if res.get("status") == "ok":
                total = res.get("total", 0.0)
                # try to generate PDF voucher if supported
                try:
                    venta_id = res.get("venta_id")
                    # Pasar el método de pago a la función generar_voucher_pdf
                    generar_voucher_pdf(venta_id or '0', self.carrito, total, self.metodo_pago)
                except Exception as e:
                    print(f"Error al generar voucher: {e}")
                messagebox.showinfo("Venta finalizada", 
                                  f"Total: S/ {total:.2f}\n"
                                  f"Método: {self.metodo_pago}\n"
                                  f"Voucher generado correctamente.")
                self.carrito = []
                self._refresh_carrito()
            else:
                messagebox.showwarning("Error", res.get("mensaje", "Error al procesar venta"))
        else:
            # assume tuple (venta_id, total)
            try:
                venta_id, total = res
            except Exception:
                messagebox.showwarning("Error", "Respuesta de venta inesperada")
                return
            # try to generate PDF voucher
            try:
                # Pasar el método de pago a la función generar_voucher_pdf
                generar_voucher_pdf(venta_id, self.carrito, total, self.metodo_pago)
            except Exception as e:
                print(f"Error al generar voucher: {e}")
            messagebox.showinfo("Venta finalizada", 
                              f"Total: S/ {total:.2f}\n"
                              f"Método: {self.metodo_pago}\n"
                              f"Voucher generado correctamente.")
            self.carrito = []
            self._refresh_carrito()

    # ---------------- ADMIN ----------------
    def abrir_admin(self):
        admin = tk.Toplevel(self.root)
        admin.title('Administrar productos')
        admin.geometry('1000x400')

        tree = ttk.Treeview(admin, columns=('id','codigo','nombre','precio','stock'), show='headings')
        tree.heading('id', text='ID')
        tree.heading('codigo', text='Codigo')
        tree.heading('nombre', text='Nombre')
        tree.heading('precio', text='Precio')
        tree.heading('stock', text='Stock')
        tree.pack(fill='both', expand=True)

        def cargar():
            for r in tree.get_children():
                tree.delete(r)
            for reg in self.db.listar_productos():
                pid, codigo, nombre, precio, stock = reg
                tree.insert('', 'end', values=(pid, codigo, nombre, f'S/ {precio:.2f}', stock))
        def agregar_manual():
            codigo = simpledialog.askstring('Codigo', 'Código de barras:')
            if not codigo:
                return
            nombre = simpledialog.askstring('Nombre', 'Nombre del producto:')
            if not nombre:
                return
            try:
                precio = float(simpledialog.askstring('Precio', 'Precio:'))
            except Exception:
                messagebox.showwarning('Aviso', 'Precio inválido')
                return
            try:
                stock = int(simpledialog.askstring('Stock', 'Stock:'))
            except Exception:
                stock = 0
            ok = self.db.agregar_producto(codigo, nombre, float(precio), int(stock))
            if ok:
                messagebox.showinfo('Ok', 'Producto agregado')
                cargar()
            else:
                messagebox.showerror('Error', 'Código ya existe')
        def editar_sel():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])['values']
            pid = vals[0]
            nombre = simpledialog.askstring('Nombre', 'Nombre:', initialvalue=vals[2])
            try:
                precio = float(simpledialog.askstring('Precio', 'Precio:', initialvalue=float(vals[3].replace('S/ ','').strip())))
            except Exception:
                messagebox.showwarning('Aviso', 'Precio inválido')
                return
            try:
                stock = int(simpledialog.askstring('Stock', 'Stock:', initialvalue=int(vals[4])))
            except Exception:
                stock = 0
            self.db.editar_producto(pid, nombre, precio, stock)
            cargar()
        def eliminar_sel():
            sel = tree.selection()
            if not sel:
                return
            vals = tree.item(sel[0])['values']
            pid = vals[0]
            if messagebox.askyesno('Confirmar', 'Eliminar producto?'):
                self.db.eliminar_producto(pid)
                cargar()

        btns = tk.Frame(admin)
        btns.pack(fill='x')
        tk.Button(btns, text='Agregar', command=agregar_manual).pack(side='left', padx=6)
        tk.Button(btns, text='Editar', command=editar_sel).pack(side='left', padx=6)
        tk.Button(btns, text='Eliminar', command=eliminar_sel).pack(side='left', padx=6)

        cargar()
        
    # ---------------- VOUCHERS / BOLETAS ----------------
    def abrir_vouchers(self):
        """Abre una ventana que lista los vouchers (PDF/TXT) generados y permite abrir/imprimir."""
        import os, webbrowser, subprocess, platform

        win = tk.Toplevel(self.root)
        win.title('Vouchers / Boletas')
        win.geometry('800x400')

        tree = ttk.Treeview(win, columns=('nombre','ruta','fecha','tam'), show='headings')
        tree.heading('nombre', text='Nombre')
        tree.heading('ruta', text='Ruta')
        tree.heading('fecha', text='Fecha mod.')
        tree.heading('tam', text='Tamaño (KB)')
        tree.pack(fill='both', expand=True)

        def listar_archivos():
            # Buscar en carpetas boletas y vouchers
            carpetas = ['boletas', 'vouchers']
            archivos = []
            for c in carpetas:
                if os.path.exists(c) and os.path.isdir(c):
                    for f in os.listdir(c):
                        fp = os.path.join(c, f)
                        if os.path.isfile(fp):
                            stat = os.stat(fp)
                            archivos.append((f, fp, stat.st_mtime, stat.st_size))
            # ordenar por fecha mod desc
            archivos.sort(key=lambda x: x[2], reverse=True)
            for r in tree.get_children():
                tree.delete(r)
            for nombre, ruta, mtime, size in archivos:
                tree.insert('', 'end', values=(nombre, ruta, datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'), f"{size//1024}"))

        def abrir_sel():
            sel = tree.selection()
            if not sel:
                return
            ruta = tree.item(sel[0])['values'][1]
            # En Windows, os.startfile abre con la app por defecto
            try:
                if platform.system() == 'Windows':
                    os.startfile(ruta)
                else:
                    webbrowser.open(ruta)
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo abrir el archivo: {e}')

        def imprimir_sel():
            sel = tree.selection()
            if not sel:
                return
            ruta = tree.item(sel[0])['values'][1]
            try:
                if platform.system() == 'Windows':
                    # 'print' con startfile manda a la impresora por defecto
                    os.startfile(ruta, 'print')
                else:
                    # En Linux/Mac intento lpr
                    subprocess.run(['lpr', ruta])
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo imprimir: {e}')

        btns = tk.Frame(win)
        btns.pack(fill='x')
        tk.Button(btns, text='Abrir', command=abrir_sel).pack(side='left', padx=6)
        tk.Button(btns, text='Imprimir', command=imprimir_sel).pack(side='left', padx=6)
        tk.Button(btns, text='Refrescar', command=listar_archivos).pack(side='left', padx=6)

        listar_archivos()
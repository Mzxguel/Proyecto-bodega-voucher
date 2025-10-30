import sqlite3
from tkinter import messagebox

class DBManager:
    def __init__(self, db_path="database/productos.db"):
        self.db_path = db_path

    def conectar(self):
        return sqlite3.connect(self.db_path)

    # ✅ Agregar producto
    def agregar_producto(self, codigo, nombre, precio, stock):
        # Validación de datos
        if not nombre or precio <= 0 or stock < 0:
            messagebox.showwarning("Datos inválidos", "Completa todos los campos correctamente.")
            return False

        # Confirmar acción
        confirmar = messagebox.askyesno("Confirmar", f"¿Deseas agregar el producto '{nombre}'?")
        if not confirmar:
            messagebox.showinfo("Cancelado", "Operación cancelada.")
            return False

        # Guardar en la base de datos
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO productos (codigo, nombre, precio, stock)
                VALUES (?, ?, ?, ?)
            ''', (codigo, nombre, precio, stock))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un producto con ese código.")
            return False
        finally:
            conn.close()


    # ✅ Listar productos
    def listar_productos(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, precio, stock FROM productos")
        productos = cursor.fetchall()
        conn.close()
        return productos

    # ✅ Buscar producto por código de barras (para modo "Vender")
    def buscar_por_codigo(self, codigo):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
        producto = cursor.fetchone()
        conn.close()
        return producto

    # ✅ Actualizar stock (después de una venta)
    def actualizar_stock(self, codigo, cantidad_vendida):
        """
        Resta la cantidad vendida al stock actual del producto.
        cantidad_vendida debe ser positiva (se resta internamente).
        """
        conn = self.conectar()
        cursor = conn.cursor()

        # Obtener el stock actual
        cursor.execute("SELECT stock FROM productos WHERE codigo = ?", (codigo,))
        producto = cursor.fetchone()

        if producto is None:
            conn.close()
            print(f"⚠️ No se encontró producto con código {codigo}")
            return

        stock_actual = producto[0]
        nuevo_stock = stock_actual - cantidad_vendida

        if nuevo_stock < 0:
            nuevo_stock = 0  # Evitar stock negativo

        # Actualizar stock en la BD
        cursor.execute("UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo))
        conn.commit()
        conn.close()

        print(f"✅ Stock actualizado para código {codigo}: {stock_actual} → {nuevo_stock}")

    
    # ✅ Eliminar producto por ID
    def eliminar_producto(self, producto_id):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        conn.commit()
        conn.close()
        return True

    # ✅ Editar producto (actualizar nombre, precio o stock)
    def editar_producto(self, producto_id, nombre, precio, stock):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre = ?, precio = ?, stock = ?
            WHERE id = ?
        """, (nombre, precio, stock, producto_id))
        conn.commit()
        conn.close()
        return True
    
    def obtener_producto_por_codigo(self, codigo):
        """Busca un producto por su código de barras."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
        producto = c.fetchone()
        conn.close()
        return producto
    
    def reducir_stock_por_id(self, producto_id, cantidad_vendida):
        """Reduce el stock de un producto en base a su ID."""
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT stock FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()

        if producto is None:
            print(f"⚠️ Producto con ID {producto_id} no encontrado.")
            conn.close()
            return

        stock_actual = producto[0]
        nuevo_stock = max(0, stock_actual - cantidad_vendida)

        cursor.execute("UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))
        conn.commit()
        conn.close()

        print(f"🟢 Stock actualizado: ID {producto_id} → {stock_actual} - {cantidad_vendida} = {nuevo_stock}")

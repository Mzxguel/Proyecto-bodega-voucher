import sqlite3


DB = 'database/productos.db'


def crear_bd():
    conn = sqlite3.connect(DB)
    c = conn.cursor()


    c.execute('''
    CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    precio REAL NOT NULL,
    stock INTEGER DEFAULT 0
    )
    ''')


    c.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    total REAL
    )
    ''')


    c.execute('''
    CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER,
    subtotal REAL,
    FOREIGN KEY(venta_id) REFERENCES ventas(id),
    FOREIGN KEY(producto_id) REFERENCES productos(id)
    )
    ''')


    conn.commit()
    conn.close()
    print('✅ Base de datos creada en', DB)


if __name__ == '__main__':
    import os
    os.makedirs('database', exist_ok=True)
    crear_bd()
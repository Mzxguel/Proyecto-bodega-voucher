from datetime import datetime
from .db_manager import DBManager


class VentasManager:
    def __init__(self, db: DBManager):
        self.db = db

def procesar_venta(self, carrito: list):
    """carrito: list of dicts {producto_id, nombre, cantidad, precio}
    Devuelve: venta_id, total
    """
    total = 0.0
    detalles = []
    for item in carrito:
        subtotal = item['cantidad'] * item['precio']
        total += subtotal
        detalles.append((item['producto_id'], item['cantidad'], subtotal))


    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    venta_id = self.db.registrar_venta(detalles, fecha, total)
    return venta_id, total
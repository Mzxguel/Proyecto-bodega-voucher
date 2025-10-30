import os
from datetime import datetime
from .printer import generar_voucher_pdf  # Importa la función PDF

class VentasManager:
    def __init__(self, db=None):
        self.db = db
        self.historial_ventas = []
        self.venta_counter = 1  # Contador para IDs de venta

    def procesar_venta(self, carrito, metodo_pago="EFECTIVO"):
        """Procesa una venta, guarda el historial y genera un voucher PDF."""
        if not carrito:
            return {"status": "error", "mensaje": "El carrito está vacío"}

        total = sum(p["precio"] * p["cantidad"] for p in carrito)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # ✅ Actualizar stock en la base de datos
        if self.db:
            for item in carrito:
                try:
                    producto_id = item.get("producto_id")  # clave esperada
                    cantidad_vendida = item.get("cantidad", 0)

                    if producto_id is not None and cantidad_vendida > 0:
                        self.db.reducir_stock_por_id(producto_id, cantidad_vendida)
                    else:
                        print(f"⚠️ No se pudo actualizar stock para {item}")
                except Exception as e:
                    print(f"⚠️ Error al actualizar stock: {e}")

        # ✅ Crear el registro de la venta
        venta_id = self.venta_counter
        self.venta_counter += 1

        venta = {
            "venta_id": venta_id,
            "fecha": fecha,
            "items": carrito.copy(),
            "total": total,
            "metodo_pago": metodo_pago
        }

        self.historial_ventas.append(venta)

        # ✅ Generar el voucher PDF
        try:
            archivo_pdf = generar_voucher_pdf(venta_id, carrito, total, metodo_pago)
        except Exception as e:
            print(f"⚠️ Error al generar PDF: {e}")
            self._generar_voucher_txt(venta)  # Fallback

        return {
            "status": "ok",
            "mensaje": "Venta procesada con éxito",
            "total": total,
            "venta_id": venta_id
        }
    
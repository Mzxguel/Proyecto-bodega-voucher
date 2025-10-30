from fpdf import FPDF
from datetime import datetime
import os

def generar_voucher_pdf(venta_id, carrito, total, metodo_pago):
    """
    Genera un voucher PDF elegante y bien formateado tipo ticket.
    """
    try:
        os.makedirs("boletas", exist_ok=True)

        fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_pdf = f"boletas/voucher_{venta_id}_{fecha}.pdf"

        # 🧾 Tamaño ticket estándar (80mm de ancho)
        pdf = FPDF("P", "mm", (80, 200))
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=5)
        pdf.set_left_margin(4)
        pdf.set_right_margin(4)

        # 🎨 COLORES (escala de grises elegante)
        COLOR_OSCURO = 40
        COLOR_MEDIO = 100
        COLOR_CLARO = 200

        # 🏪 ENCABEZADO ELEGANTE
        pdf.set_fill_color(COLOR_OSCURO)
        pdf.set_text_color(255)  # Blanco
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "BODEGA SILMIG", ln=True, align="C", fill=True)
        
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 5, "Tu bodega de confianza", ln=True, align="C", fill=True)
        
        pdf.set_fill_color(COLOR_CLARO)
        pdf.set_text_color(0)  # Negro

        # 📅 FECHA Y HORA
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        pdf.cell(0, 5, f"Fecha: {fecha_hora}", ln=True, align="C", fill=True)

        # 🛒 TABLA DE PRODUCTOS - ENCABEZADO
        pdf.set_fill_color(COLOR_MEDIO)
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(30, 5, "PRODUCTO", border=0, fill=True)
        pdf.cell(8, 5, "CANT", border=0, align="C", fill=True)
        pdf.cell(15, 5, "PRECIO", border=0, align="R", fill=True)
        pdf.cell(19, 5, "SUBTOTAL", border=0, align="R", ln=True, fill=True)

        # 📝 DETALLE DE PRODUCTOS
        pdf.set_fill_color(COLOR_CLARO)
        pdf.set_text_color(0)
        pdf.set_font("Arial", "", 7)

        for item in carrito:
            nombre = item["nombre"]
            cantidad = item["cantidad"]
            precio = item["precio"]
            subtotal = cantidad * precio

            # 🔹 Ajustar nombre largo (máximo 2 líneas)
            nombre_ajustado = nombre
            if len(nombre) > 24:
                palabras = nombre.split()
                linea1 = ""
                linea2 = ""
                
                for palabra in palabras:
                    if len(linea1 + " " + palabra) <= 24 and not linea2:
                        linea1 += " " + palabra if linea1 else palabra
                    else:
                        linea2 += " " + palabra if linea2 else palabra
                
                if len(linea2) > 21:
                    linea2 = linea2[:21] + "..."
                
                nombre_ajustado = linea1.strip()
                if linea2:
                    nombre_ajustado += "\n" + linea2.strip()

            lineas = nombre_ajustado.count('\n') + 1
            altura_celda = 4 * lineas

            pdf.set_fill_color(255)
            pdf.cell(30, altura_celda, nombre_ajustado, border=0, align="L")
            pdf.cell(8, altura_celda, str(cantidad), border=0, align="C")
            pdf.cell(15, altura_celda, f"S/{precio:.2f}", border=0, align="R")
            pdf.cell(19, altura_celda, f"S/{subtotal:.2f}", border=0, align="R", ln=True)

        # 💰 TOTALES
        pdf.set_fill_color(COLOR_MEDIO)
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(53, 6, "TOTAL A PAGAR:", border=0, align="R", fill=True)
        pdf.cell(19, 6, f"S/{total:.2f}", border=0, align="R", ln=True, fill=True)

        # 💳 MÉTODO DE PAGO (usar texto en lugar de emojis para evitar problemas de encoding)
        pdf.set_fill_color(COLOR_CLARO)
        pdf.set_text_color(0)
        pdf.set_font("Arial", "B", 9)
        
        # Usar texto en lugar de emojis
        texto_pago = f"Metodo de pago: {metodo_pago}"
        pdf.cell(0, 6, texto_pago, ln=True, align="C", fill=True)

        # 📞 INFORMACIÓN DE CONTACTO
        pdf.set_font("Arial", "", 7)
        pdf.cell(0, 3, "Tel: 938712448", ln=True, align="C")

        # ❤️ MENSAJE FINAL
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 8, "¡Gracias por tu compra!", ln=True, align="C")
        pdf.set_font("Arial", "", 7)
        pdf.cell(0, 4, "Vuelve pronto a SILMIG", ln=True, align="C")

        # ⚠️ INFORMACIÓN LEGAL
        pdf.set_font("Arial", "", 6)
        pdf.multi_cell(0, 2, 
            "No se aceptan devoluciones.", 
            align="C")

        # 📄 GUARDAR PDF
        pdf.output(nombre_pdf)

        return nombre_pdf

    except Exception as e:
        print(f"❌ Error al generar PDF: {e}")
        raise e
import csv
from pathlib import Path
from datetime import datetime

class ReportService:
    def __init__(self, catalog, checkout, repository):
        self.catalog, self.checkout, self.repository = catalog, checkout, repository

    def export_orders_csv(self, destination):
        path = Path(destination)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Pedido", "Cliente", "Fecha", "Estado", "Subtotal descuento", "Descuento", "Total", "Codigo"])
            for o in self.checkout.history():
                subtotal = sum(i.unit_price*i.quantity for i in o.items)
                writer.writerow([o.id, o.customer, o.created_at, o.status, subtotal, o.discount_amount, o.total, o.discount_code])
        return path

    def export_products_csv(self, destination):
        path = Path(destination)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f); writer.writerow(["ID", "Nombre", "Categoria", "Precio COP", "Stock"])
            for p in self.catalog.all(): writer.writerow([p.id,p.name,p.category,p.price,p.stock])
        return path

    def receipt_pdf(self, order, destination):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError as exc:
            raise RuntimeError("Para generar comprobantes instala ReportLab: python -m pip install reportlab") from exc
        path = Path(destination)
        c = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 55
        c.setTitle(f"Comprobante ShopFlow {order.id}")
        c.setFont("Helvetica-Bold", 20); c.drawString(48, y, "SHOPFLOW")
        y -= 28; c.setFont("Helvetica", 10); c.drawString(48, y, "Comprobante de pedido - Pago simulado")
        y -= 35
        c.setFont("Helvetica-Bold", 11); c.drawString(48, y, f"Pedido: {order.id}")
        y -= 18; c.setFont("Helvetica", 10)
        c.drawString(48, y, f"Cliente: {order.customer}")
        y -= 16; c.drawString(48, y, f"Fecha: {order.created_at}")
        y -= 16; c.drawString(48, y, f"Estado: {order.status}")
        y -= 30
        c.setFont("Helvetica-Bold", 10)
        c.drawString(48, y, "Producto"); c.drawString(300, y, "Cant."); c.drawString(360, y, "Precio"); c.drawString(455, y, "Subtotal")
        y -= 10; c.line(48, y, width-48, y); y -= 18
        c.setFont("Helvetica", 9)
        subtotal = 0
        for item in order.items:
            if y < 90: c.showPage(); y = height - 55
            line_total = item.unit_price * item.quantity; subtotal += line_total
            c.drawString(48, y, item.name[:42])
            c.drawRightString(330, y, str(item.quantity))
            c.drawRightString(420, y, f"${item.unit_price:,.0f}")
            c.drawRightString(width-48, y, f"${line_total:,.0f}")
            y -= 18
        y -= 10; c.line(300, y, width-48, y); y -= 20
        c.drawRightString(width-48, y, f"Subtotal: ${subtotal:,.0f}"); y -= 18
        c.drawRightString(width-48, y, f"Descuento: -${order.discount_amount:,.0f}"); y -= 22
        c.setFont("Helvetica-Bold", 13); c.drawRightString(width-48, y, f"TOTAL: ${order.total:,.0f}")
        y -= 45; c.setFont("Helvetica-Oblique", 9)
        c.drawString(48, y, "Este documento es un comprobante académico. No representa un cobro bancario real.")
        c.save()
        return path

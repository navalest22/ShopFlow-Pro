from datetime import datetime
from domain.models import Order, OrderItem
from structures.queue import Queue

class CheckoutService:
    """Reserva inventario al confirmar; procesa y cancela pedidos respetando FIFO."""
    def __init__(self, repository, catalog, cart, customers=None, promotions=None):
        self.repository, self.catalog, self.cart = repository, catalog, cart
        self.customers, self.promotions = customers, promotions
        self.queue, self.orders = Queue(), []
        self._load()
    def _load(self):
        state = self.repository.load()
        self.orders = [Order.from_dict(x) for x in state["orders"]]
        for raw in state["payment_queue"]: self.queue.enqueue(Order.from_dict(raw))
    def _persist_all(self):
        state = self.repository.load()
        state["products"] = [p.to_dict() for p in self.catalog.all()]
        state["cart"] = [{"product_id": pid, "quantity": qty} for pid, qty in self.cart.items.items()]
        state["orders"] = [o.to_dict() for o in self.orders]
        state["payment_queue"] = [o.to_dict() for o in self.queue.to_list()]
        self.repository.save(state)
    def submit(self, customer, phone="", email="", discount_code=""):
        lines, subtotal = self.cart.lines()
        if not lines: raise ValueError("El carrito está vacío.")
        for p, qty, _ in lines:
            if qty > p.stock: raise ValueError(f"Stock insuficiente para {p.name}.")
        customer_record = self.customers.get_or_create(customer, phone, email) if self.customers else None
        discount = 0.0; applied_code = ""
        if discount_code and self.promotions:
            promo = self.promotions.find_active(discount_code)
            if not promo: raise ValueError("El código de descuento no existe o está inactivo.")
            applied_code = promo["code"]; discount = round(subtotal * promo["percent"] / 100, 2)
        order = Order(Order.new_id(), customer.strip(), datetime.now().isoformat(timespec="seconds"),
                      [OrderItem(p.id, p.name, p.price, qty) for p, qty, _ in lines],
                      round(subtotal-discount, 2), "PENDIENTE", applied_code, discount)
        for p, qty, _ in lines:
            p.stock -= qty
            self.catalog.record_movement(p.id, "RESERVA", qty, f"Pedido {order.id}")
        self.queue.enqueue(order)
        self.cart.items = {}; self.cart.undo_stack.clear(); self.cart.redo_stack.clear()
        self._persist_all()
        return order
    def process_next(self):
        order = self.queue.dequeue()
        if order is None: return None
        order.status = "PAGADO"
        self.orders.append(order)
        self._persist_all()
        return order
    def cancel(self, order_id):
        pending = self.queue.to_list()
        order = next((o for o in pending if o.id == order_id), None)
        if not order: raise ValueError("Solo se pueden cancelar pedidos pendientes.")
        rebuilt = Queue()
        for item in pending:
            if item.id != order_id: rebuilt.enqueue(item)
        self.queue = rebuilt
        order.status = "CANCELADO"
        self.orders.append(order)
        for item in order.items:
            p = self.catalog.get(item.product_id)
            if p:
                p.stock += item.quantity
                self.catalog.record_movement(p.id, "REINTEGRO", item.quantity, f"Cancelación pedido {order.id}")
        self._persist_all()
        return order
    def pending(self): return self.queue.to_list()
    def history(self): return list(reversed(self.orders))
    def find(self, term):
        term = term.strip().casefold()
        all_orders = self.history() + list(reversed(self.pending()))
        return [o for o in all_orders if not term or term in o.id.casefold() or term in o.customer.casefold() or term in o.status.casefold()]
    def get(self, order_id):
        return next((o for o in self.history() + self.pending() if o.id == order_id), None)
    def stats(self):
        paid = [o for o in self.orders if o.status == "PAGADO"]
        return {"orders":len(self.orders)+len(self.pending()), "paid":len(paid),
                "pending":len(self.pending()), "cancelled":sum(o.status=="CANCELADO" for o in self.orders),
                "revenue":sum(o.total for o in paid), "average":sum(o.total for o in paid)/len(paid) if paid else 0}

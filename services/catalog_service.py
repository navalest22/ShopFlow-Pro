from datetime import datetime
from domain.models import Product
from structures.avl_tree import AVLTree

class CatalogService:
    def __init__(self, repository):
        self.repository = repository
        self.products = {}
        self.index = AVLTree()
        self._load()

    def _rebuild_index(self):
        self.index = AVLTree()
        for p in self.products.values(): self.index.insert(p.name, p)

    def _load(self):
        for raw in self.repository.load()["products"]:
            try:
                p = Product.from_dict(raw); self.products[p.id] = p
            except (TypeError, KeyError): continue
        self._rebuild_index()
        if not self.products: self._seed()

    def _seed(self):
        demo = [
            Product("P001", "Audifonos Bluetooth", "Tecnologia", 89900, 12),
            Product("P002", "Mouse Gamer", "Tecnologia", 65000, 20),
            Product("P003", "Teclado Mecanico", "Tecnologia", 189900, 8),
            Product("P004", "Camiseta Basica", "Ropa", 45000, 30),
            Product("P005", "Mochila Urbana", "Accesorios", 120000, 15),
            Product("P006", "Parlante Portatil", "Tecnologia", 139900, 7)]
        self.products = {p.id: p for p in demo}
        self._rebuild_index(); self._persist()

    def _persist(self):
        state = self.repository.load()
        state["products"] = [p.to_dict() for p in self.products.values()]
        self.repository.save(state)

    def all(self): return sorted(self.products.values(), key=lambda p: p.name.casefold())
    def get(self, product_id): return self.products.get(product_id)
    def search(self, name): return self.index.search(name) if name.strip() else []

    def _next_id(self):
        numbers = [int(k[1:]) for k in self.products if k.startswith("P") and k[1:].isdigit()]
        return f"P{max(numbers + [0]) + 1:03d}"

    def add(self, name, category, price, stock):
        name = name.strip()
        if not name or float(price) <= 0 or int(stock) < 0: raise ValueError("Nombre, precio o stock no válido.")
        p = Product(self._next_id(), name, category.strip() or "General", float(price), int(stock))
        self.products[p.id] = p; self._rebuild_index(); self._persist()
        self.record_movement(p.id, "ENTRADA INICIAL", p.stock, "Creación de producto")
        self._persist(); return p

    def update(self, product_id, name, category, price):
        p = self.get(product_id)
        if not p: raise ValueError("Producto inexistente.")
        if not name.strip() or float(price) <= 0: raise ValueError("Nombre y precio deben ser válidos.")
        p.name, p.category, p.price = name.strip(), category.strip() or "General", float(price)
        self._rebuild_index(); self._persist(); return p

    def delete(self, product_id, cart_ids=None, pending_ids=None):
        if product_id not in self.products: raise ValueError("Producto inexistente.")
        if product_id in (cart_ids or set()): raise ValueError("No se puede eliminar: el producto está en un carrito.")
        if product_id in (pending_ids or set()): raise ValueError("No se puede eliminar: aparece en un pedido pendiente.")
        del self.products[product_id]
        self._rebuild_index(); self._persist()

    def adjust_stock(self, product_id, delta, reason="Ajuste manual"):
        p = self.get(product_id)
        if not p: raise ValueError("Producto inexistente.")
        delta = int(delta)
        if p.stock + delta < 0: raise ValueError("El inventario no puede quedar negativo.")
        p.stock += delta
        self.record_movement(product_id, "ENTRADA" if delta >= 0 else "SALIDA", abs(delta), reason)
        self._persist()
        return p

    def record_movement(self, product_id, movement_type, quantity, reason, persist=True):
        state = self.repository.load()
        state["inventory_movements"].append({
            "id": f"M{len(state['inventory_movements']) + 1:06d}",
            "product_id": product_id, "product_name": self.get(product_id).name if self.get(product_id) else product_id,
            "type": movement_type, "quantity": int(quantity), "reason": reason,
            "date": datetime.now().isoformat(timespec="seconds")})
        if persist: self.repository.save(state)

    def movements(self):
        return list(reversed(self.repository.load()["inventory_movements"]))

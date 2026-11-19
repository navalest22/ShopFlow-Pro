from copy import deepcopy
from structures.stack import Stack

class CartService:
    def __init__(self, repository, catalog):
        self.repository, self.catalog = repository, catalog
        self.items = {}; self.undo_stack, self.redo_stack = Stack(), Stack()
        self._load()
    def _load(self):
        self.items = {x["product_id"]: int(x["quantity"]) for x in self.repository.load()["cart"]}
    def _save(self):
        state = self.repository.load()
        state["cart"] = [{"product_id": pid, "quantity": qty} for pid, qty in self.items.items()]
        self.repository.save(state)
    def _change(self, operation):
        before = deepcopy(self.items); operation()
        self.undo_stack.push(before); self.redo_stack.clear(); self._save()
    def add(self, product_id, quantity=1):
        p = self.catalog.get(product_id)
        if not p: raise ValueError("Producto inexistente.")
        if quantity <= 0: raise ValueError("La cantidad debe ser mayor que cero.")
        new_qty = self.items.get(product_id, 0) + quantity
        if new_qty > p.stock: raise ValueError(f"Stock disponible: {max(0, p.stock - self.items.get(product_id, 0))}")
        self._change(lambda: self.items.__setitem__(product_id, new_qty))
    def set_quantity(self, product_id, quantity):
        if product_id not in self.items: raise ValueError("El producto no está en el carrito.")
        if quantity < 0: raise ValueError("Cantidad inválida.")
        p = self.catalog.get(product_id)
        if not p: raise ValueError("Producto inexistente.")
        if quantity > p.stock: raise ValueError(f"Stock máximo: {p.stock}")
        def op():
            if quantity == 0: self.items.pop(product_id, None)
            else: self.items[product_id] = quantity
        self._change(op)
    def remove(self, product_id):
        if product_id not in self.items: raise ValueError("El producto no está en el carrito.")
        self._change(lambda: self.items.pop(product_id))
    def undo(self):
        previous = self.undo_stack.pop()
        if previous is None: return False
        self.redo_stack.push(deepcopy(self.items)); self.items = previous; self._save(); return True
    def redo(self):
        following = self.redo_stack.pop()
        if following is None: return False
        self.undo_stack.push(deepcopy(self.items)); self.items = following; self._save(); return True
    def clear(self): self.items = {}; self.undo_stack.clear(); self.redo_stack.clear(); self._save()
    def lines(self):
        result, total = [], 0
        for pid, qty in self.items.items():
            p = self.catalog.get(pid)
            if p:
                subtotal = p.price * qty; total += subtotal; result.append((p, qty, subtotal))
        return result, total

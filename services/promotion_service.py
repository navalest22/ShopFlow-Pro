from datetime import date
class PromotionService:
    def __init__(self, repository): self.repository = repository
    def all(self): return self.repository.load()["promotions"]
    def create(self, code, percent, active=True):
        code = code.strip().upper()
        if not code or not 1 <= float(percent) <= 90: raise ValueError("Código obligatorio y descuento entre 1% y 90%.")
        state = self.repository.load()
        if any(x["code"] == code for x in state["promotions"]): raise ValueError("Ese código ya existe.")
        promo = {"code": code, "percent": float(percent), "active": bool(active), "created_at": date.today().isoformat()}
        state["promotions"].append(promo); self.repository.save(state); return promo
    def find_active(self, code):
        return next((x for x in self.all() if x["code"] == code.strip().upper() and x["active"]), None)
    def toggle(self, code):
        state = self.repository.load()
        p = next((x for x in state["promotions"] if x["code"] == code), None)
        if not p: raise ValueError("Promoción no encontrada.")
        p["active"] = not p["active"]; self.repository.save(state); return p

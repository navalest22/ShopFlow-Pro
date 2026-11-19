from datetime import datetime
class CustomerService:
    def __init__(self, repository): self.repository = repository
    def all(self): return self.repository.load()["customers"]
    def get_or_create(self, name, phone="", email=""):
        name = name.strip()
        if not name: raise ValueError("El nombre del cliente es obligatorio.")
        state = self.repository.load()
        for c in state["customers"]:
            if c["name"].casefold() == name.casefold():
                if phone: c["phone"] = phone.strip()
                if email: c["email"] = email.strip()
                self.repository.save(state); return c
        customer = {"id": f"C{len(state['customers'])+1:04d}", "name": name,
                    "phone": phone.strip(), "email": email.strip(),
                    "created_at": datetime.now().isoformat(timespec="seconds")}
        state["customers"].append(customer); self.repository.save(state); return customer
    def update(self, customer_id, name, phone, email):
        state = self.repository.load()
        c = next((x for x in state["customers"] if x["id"] == customer_id), None)
        if not c: raise ValueError("Cliente no encontrado.")
        if not name.strip(): raise ValueError("El nombre es obligatorio.")
        c.update(name=name.strip(), phone=phone.strip(), email=email.strip())
        self.repository.save(state); return c

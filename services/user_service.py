import hashlib, hmac, os
ROLES = {"ADMIN": {"all"}, "INVENTARIO": {"products", "inventory", "dashboard"},
         "VENTAS": {"cart", "orders", "customers", "promotions", "dashboard"}}
class UserService:
    def __init__(self, repository):
        self.repository = repository
        self._ensure_admin()
    @staticmethod
    def _hash(password, salt=None):
        salt = salt or os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 180000).hex()
        return salt, digest
    def _ensure_admin(self):
        state = self.repository.load()
        if not state["users"]:
            salt, digest = self._hash("ShopFlow2026*")
            state["users"].append({"username":"admin", "salt":salt, "password_hash":digest, "role":"ADMIN", "active":True})
            self.repository.save(state)
    def authenticate(self, username, password):
        state = self.repository.load()
        user = next((u for u in state["users"] if u["username"].casefold() == username.strip().casefold() and u.get("active", True)), None)
        if not user: return None
        _, digest = self._hash(password, user["salt"])
        return user if hmac.compare_digest(digest, user["password_hash"]) else None
    def all(self):
        return [{k:v for k,v in u.items() if k not in ("salt","password_hash")} for u in self.repository.load()["users"]]
    def create(self, username, password, role):
        username = username.strip()
        if len(username) < 3 or len(password) < 8: raise ValueError("Usuario mínimo 3 caracteres y contraseña mínimo 8.")
        if role not in ROLES: raise ValueError("Rol no válido.")
        state = self.repository.load()
        if any(u["username"].casefold() == username.casefold() for u in state["users"]): raise ValueError("El usuario ya existe.")
        salt, digest = self._hash(password)
        state["users"].append({"username":username, "salt":salt, "password_hash":digest, "role":role, "active":True})
        self.repository.save(state)
    def allowed(self, user, permission):
        return user and (user["role"] == "ADMIN" or permission in ROLES.get(user["role"], set()))

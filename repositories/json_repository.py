import json, os
from pathlib import Path
from threading import RLock

class JSONRepository:
    """Almacenamiento JSON con escritura atómica y migración de esquema."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        if not self.path.exists(): self.save(self.default_state())

    @staticmethod
    def default_state():
        return {"schema_version": 2, "products": [], "cart": [], "orders": [],
                "payment_queue": [], "customers": [], "inventory_movements": [],
                "promotions": [], "users": [], "audit_log": []}

    def load(self):
        with self._lock:
            try:
                with self.path.open("r", encoding="utf-8") as f: data = json.load(f)
            except (json.JSONDecodeError, OSError):
                # No sobrescribe silenciosamente un archivo corrupto.
                backup = self.path.with_suffix(self.path.suffix + ".corrupt")
                if self.path.exists() and not backup.exists():
                    try: os.replace(self.path, backup)
                    except OSError: pass
                data = self.default_state()
            if not isinstance(data, dict): data = self.default_state()
            for key, value in self.default_state().items(): data.setdefault(key, value)
            data["schema_version"] = 2
            return data

    def save(self, state):
        with self._lock:
            temp = self.path.with_suffix(self.path.suffix + ".tmp")
            with temp.open("w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush(); os.fsync(f.fileno())
            os.replace(temp, self.path)

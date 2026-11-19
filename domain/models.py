from dataclasses import dataclass, asdict
from uuid import uuid4

@dataclass
class Product:
    id: str
    name: str
    category: str
    price: float
    stock: int
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, data): return cls(**data)

@dataclass
class OrderItem:
    product_id: str
    name: str
    unit_price: float
    quantity: int
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, data): return cls(**data)

@dataclass
class Order:
    id: str
    customer: str
    created_at: str
    items: list
    total: float
    status: str = "PENDIENTE"
    discount_code: str = ""
    discount_amount: float = 0.0
    def to_dict(self):
        data = asdict(self)
        data["items"] = [x.to_dict() if hasattr(x, "to_dict") else x for x in self.items]
        return data
    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], customer=data["customer"], created_at=data["created_at"],
                   items=[OrderItem.from_dict(x) for x in data.get("items", [])],
                   total=float(data.get("total", 0)), status=data.get("status", "PENDIENTE"),
                   discount_code=data.get("discount_code", ""), discount_amount=float(data.get("discount_amount", 0)))
    @staticmethod
    def new_id(): return uuid4().hex[:8].upper()

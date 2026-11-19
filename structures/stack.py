class Stack:
    """Pila LIFO propia basada en nodos enlazados."""
    class _Node:
        def __init__(self, value, nxt=None): self.value, self.next = value, nxt
    def __init__(self): self.top = None; self.size = 0
    def push(self, value): self.top = self._Node(value, self.top); self.size += 1
    def pop(self):
        if self.top is None: return None
        value = self.top.value; self.top = self.top.next; self.size -= 1; return value
    def peek(self): return self.top.value if self.top else None
    def is_empty(self): return self.top is None
    def clear(self): self.top = None; self.size = 0

class _Node:
    __slots__ = ("key", "values", "left", "right", "height")
    def __init__(self, key, value):
        self.key, self.values = key, [value]
        self.left = self.right = None
        self.height = 1

class AVLTree:
    """AVL auto-balanceado. Una clave puede contener varios productos."""
    def __init__(self): self.root = None
    def _h(self, n): return n.height if n else 0
    def _fix(self, n): n.height = 1 + max(self._h(n.left), self._h(n.right))
    def _balance(self, n): return self._h(n.left) - self._h(n.right)
    def _right(self, y):
        x, t = y.left, y.left.right
        x.right, y.left = y, t
        self._fix(y); self._fix(x)
        return x
    def _left(self, x):
        y, t = x.right, x.right.left
        y.left, x.right = x, t
        self._fix(x); self._fix(y)
        return y
    def insert(self, key, value): self.root = self._insert(self.root, key.casefold().strip(), value)
    def _insert(self, n, key, value):
        if not n: return _Node(key, value)
        if key < n.key: n.left = self._insert(n.left, key, value)
        elif key > n.key: n.right = self._insert(n.right, key, value)
        else:
            if all(getattr(v, "id", None) != getattr(value, "id", None) for v in n.values): n.values.append(value)
            return n
        self._fix(n); b = self._balance(n)
        if b > 1 and key < n.left.key: return self._right(n)
        if b < -1 and key > n.right.key: return self._left(n)
        if b > 1 and key > n.left.key:
            n.left = self._left(n.left); return self._right(n)
        if b < -1 and key < n.right.key:
            n.right = self._right(n.right); return self._left(n)
        return n
    def search(self, key):
        key = key.casefold().strip(); n = self.root
        while n:
            if key == n.key: return list(n.values)
            n = n.left if key < n.key else n.right
        return []
    def inorder(self):
        out = []
        def walk(n):
            if n: walk(n.left); out.extend(n.values); walk(n.right)
        walk(self.root); return out
    def clear(self): self.root = None

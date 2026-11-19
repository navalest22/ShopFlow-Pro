class Queue:
    """Cola FIFO propia con referencias al frente y al final."""
    class _Node:
        def __init__(self, value): self.value, self.next = value, None
    def __init__(self): self.front = self.rear = None; self.size = 0
    def enqueue(self, value):
        node = self._Node(value)
        if self.rear is None: self.front = self.rear = node
        else: self.rear.next = node; self.rear = node
        self.size += 1
    def dequeue(self):
        if self.front is None: return None
        value = self.front.value; self.front = self.front.next; self.size -= 1
        if self.front is None: self.rear = None
        return value
    def peek(self): return self.front.value if self.front else None
    def is_empty(self): return self.front is None
    def __len__(self): return self.size
    def to_list(self):
        out, node = [], self.front
        while node: out.append(node.value); node = node.next
        return out

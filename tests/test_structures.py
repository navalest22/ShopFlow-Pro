import unittest
from structures.avl_tree import AVLTree
from structures.stack import Stack
from structures.queue import Queue

class StructureTests(unittest.TestCase):
    def test_avl_search_and_order(self):
        tree = AVLTree()
        for name in ["Zebra", "Manzana", "Arbol", "Pera", "Banano"]: tree.insert(name, name)
        self.assertEqual(tree.search("manzana"), ["Manzana"])
        self.assertEqual(tree.inorder(), ["Arbol", "Banano", "Manzana", "Pera", "Zebra"])
    def test_stack_lifo(self):
        stack = Stack(); stack.push(1); stack.push(2)
        self.assertEqual(stack.pop(), 2); self.assertEqual(stack.pop(), 1); self.assertTrue(stack.is_empty())
    def test_queue_fifo(self):
        queue = Queue(); queue.enqueue("A"); queue.enqueue("B")
        self.assertEqual(queue.dequeue(), "A"); self.assertEqual(queue.dequeue(), "B"); self.assertTrue(queue.is_empty())

if __name__ == "__main__": unittest.main()

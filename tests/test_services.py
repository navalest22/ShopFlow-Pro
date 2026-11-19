import tempfile, unittest, json, csv
from pathlib import Path
from repositories.json_repository import JSONRepository
from services.catalog_service import CatalogService
from services.cart_service import CartService
from services.checkout_service import CheckoutService
from services.customer_service import CustomerService
from services.promotion_service import PromotionService
from services.user_service import UserService
from services.report_service import ReportService

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = JSONRepository(Path(self.temp.name) / "state.json")
        self.catalog = CatalogService(self.repo)
        self.cart = CartService(self.repo, self.catalog)
        self.customers = CustomerService(self.repo)
        self.promos = PromotionService(self.repo)
        self.checkout = CheckoutService(self.repo, self.catalog, self.cart, self.customers, self.promos)
    def tearDown(self): self.temp.cleanup()

    def test_cart_undo_redo(self):
        self.cart.add("P001", 2)
        self.assertTrue(self.cart.undo()); self.assertNotIn("P001", self.cart.items)
        self.assertTrue(self.cart.redo()); self.assertEqual(self.cart.items["P001"], 2)

    def test_fifo_checkout_stock_and_cancel_restore(self):
        self.cart.add("P001", 2); first = self.checkout.submit("Ana")
        self.cart.add("P002", 1); second = self.checkout.submit("Luis")
        self.assertEqual([o.id for o in self.checkout.pending()], [first.id, second.id])
        self.assertEqual(self.catalog.get("P001").stock, 10)
        cancelled = self.checkout.cancel(first.id)
        self.assertEqual(cancelled.status, "CANCELADO")
        self.assertEqual(self.catalog.get("P001").stock, 12)
        self.assertEqual([o.id for o in self.checkout.pending()], [second.id])
        self.assertEqual(self.checkout.process_next().id, second.id)
        self.assertEqual(self.catalog.get("P002").stock, 19)
        self.assertTrue(any(m["type"] == "REINTEGRO" for m in self.catalog.movements()))

    def test_cannot_cancel_paid_order(self):
        self.cart.add("P001", 1); order = self.checkout.submit("Ana")
        self.checkout.process_next()
        with self.assertRaises(ValueError): self.checkout.cancel(order.id)

    def test_product_edit_delete_and_avl_reindex(self):
        p = self.catalog.add("Producto Temporal", "Test", 1000, 5)
        self.catalog.update(p.id, "Nombre Actualizado", "Test", 2000)
        self.assertEqual(self.catalog.search("Nombre Actualizado")[0].id, p.id)
        self.assertEqual(self.catalog.search("Producto Temporal"), [])
        self.catalog.delete(p.id)
        self.assertIsNone(self.catalog.get(p.id))

    def test_inventory_movement(self):
        before = self.catalog.get("P001").stock
        self.catalog.adjust_stock("P001", 3, "Compra a proveedor")
        self.assertEqual(self.catalog.get("P001").stock, before + 3)
        self.assertEqual(self.catalog.movements()[0]["reason"], "Compra a proveedor")

    def test_promotion_and_customer(self):
        self.promos.create("BIENVENIDA10", 10)
        self.cart.add("P001", 1)
        order = self.checkout.submit("Carla", "3001234567", "carla@example.com", "BIENVENIDA10")
        self.assertEqual(order.discount_amount, 8990)
        self.assertEqual(order.total, 80910)
        self.assertEqual(self.customers.all()[0]["email"], "carla@example.com")

    def test_user_authentication_and_permissions(self):
        users = UserService(self.repo)
        admin = users.authenticate("admin", "ShopFlow2026*")
        self.assertIsNotNone(admin)
        self.assertTrue(users.allowed(admin, "all"))
        users.create("bodega", "ClaveSegura123", "INVENTARIO")
        warehouse = users.authenticate("bodega", "ClaveSegura123")
        self.assertTrue(users.allowed(warehouse, "products"))
        self.assertFalse(users.allowed(warehouse, "orders"))
        self.assertIsNone(users.authenticate("admin", "incorrecta"))

    def test_csv_exports(self):
        self.cart.add("P001", 1); self.checkout.submit("Diana"); self.checkout.process_next()
        reports = ReportService(self.catalog, self.checkout, self.repo)
        orders_path = Path(self.temp.name) / "orders.csv"
        products_path = Path(self.temp.name) / "products.csv"
        reports.export_orders_csv(orders_path); reports.export_products_csv(products_path)
        self.assertIn("Pedido", orders_path.read_text(encoding="utf-8-sig"))
        self.assertIn("P001", products_path.read_text(encoding="utf-8-sig"))


    def test_pdf_receipt(self):
        self.cart.add("P001", 1)
        order = self.checkout.submit("Fabian")
        self.checkout.process_next()
        reports = ReportService(self.catalog, self.checkout, self.repo)
        output = Path(self.temp.name) / "receipt.pdf"
        reports.receipt_pdf(order, output)
        self.assertTrue(output.exists())
        self.assertTrue(output.read_bytes().startswith(b"%PDF"))

    def test_search_orders(self):
        self.cart.add("P001", 1); order = self.checkout.submit("Elena")
        self.assertEqual(self.checkout.find("elena")[0].id, order.id)
        self.assertEqual(self.checkout.get(order.id).customer, "Elena")

if __name__ == "__main__": unittest.main()

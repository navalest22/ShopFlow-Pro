from pathlib import Path
import tkinter as tk
from repositories.json_repository import JSONRepository
from services.catalog_service import CatalogService
from services.cart_service import CartService
from services.checkout_service import CheckoutService
from services.customer_service import CustomerService
from services.promotion_service import PromotionService
from services.user_service import UserService
from services.report_service import ReportService
from ui.main_window import ShopFlowWindow

BASE_DIR = Path(__file__).resolve().parent

def main():
    repository = JSONRepository(BASE_DIR / "data" / "shopflow.json")
    catalog = CatalogService(repository)
    cart = CartService(repository, catalog)
    customers = CustomerService(repository)
    promotions = PromotionService(repository)
    checkout = CheckoutService(repository, catalog, cart, customers, promotions)
    users = UserService(repository)
    reports = ReportService(catalog, checkout, repository)
    root = tk.Tk()
    ShopFlowWindow(root, catalog, cart, checkout, customers, promotions, users, reports)
    root.mainloop()

if __name__ == "__main__":
    main()

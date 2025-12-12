import json
import os
from threading import Lock

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'catalog.json')
data_lock = Lock()


class CatalogService:
    @staticmethod
    def load_catalog():
        with data_lock:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    
    @staticmethod
    def save_catalog(catalog):
        with data_lock:
            with open(DATA_FILE, 'w') as f:
                json.dump(catalog, f, indent=2)
    
    @staticmethod
    def search_by_topic(topic):
        catalog = CatalogService.load_catalog()
        results = [
            {"id": book["id"], "title": book["title"]}
            for book in catalog
            if book["topic"].lower() == topic.lower()
        ]
        return results
    
    @staticmethod
    def get_book_info(book_id):
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                return {
                    "title": book["title"],
                    "quantity": book["quantity"],
                    "price": book["price"]
                }
        return None
    
    @staticmethod
    def decrement_quantity(book_id):
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                if book["quantity"] > 0:
                    book["quantity"] -= 1
                    CatalogService.save_catalog(catalog)
                    return True, "Quantity decremented successfully"
                else:
                    return False, "Out of stock"
        return False, "Book not found"
    
    @staticmethod
    def update_price(book_id, new_price):
        """Update the price of a book"""
        if new_price <= 0:
            return False, "Price must be greater than 0"
        
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                old_price = book["price"]
                book["price"] = new_price
                CatalogService.save_catalog(catalog)
                return True, f"Price updated from ${old_price} to ${new_price}"
        return False, "Book not found"
    
    @staticmethod
    def update_stock(book_id, quantity_change):
        """Increase or decrease stock quantity"""
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                new_quantity = book["quantity"] + quantity_change
                if new_quantity < 0:
                    return False, f"Cannot reduce stock below 0. Current: {book['quantity']}, Requested change: {quantity_change}"
                
                old_quantity = book["quantity"]
                book["quantity"] = new_quantity
                CatalogService.save_catalog(catalog)
                
                action = "increased" if quantity_change > 0 else "decreased"
                return True, f"Stock {action} from {old_quantity} to {new_quantity}"
        return False, "Book not found"

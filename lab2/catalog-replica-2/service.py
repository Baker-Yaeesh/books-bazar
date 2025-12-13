import json
import os
from threading import Lock
import sync

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
        book_topic = None
        
        for book in catalog:
            if book["id"] == book_id:
                if book["quantity"] > 0:
                    book["quantity"] -= 1
                    book_topic = book["topic"]
                    CatalogService.save_catalog(catalog)
                    
                    sync.propagate_write('decrement', book_id, {'quantity': book["quantity"]})
                    sync.invalidate_cache(book_id, [book_topic])
                    
                    return True, "Quantity decremented successfully"
                else:
                    return False, "Out of stock"
        return False, "Book not found"
    
    @staticmethod
    def update_price(book_id, new_price):
        if new_price <= 0:
            return False, "Price must be greater than 0"
        
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                old_price = book["price"]
                book["price"] = new_price
                book_topic = book["topic"]
                CatalogService.save_catalog(catalog)
                
                sync.propagate_write('update_price', book_id, {'price': new_price})
                sync.invalidate_cache(book_id, [book_topic])
                
                return True, f"Price updated from ${old_price} to ${new_price}"
        return False, "Book not found"
    
    @staticmethod
    def update_stock(book_id, quantity_change):
        catalog = CatalogService.load_catalog()
        for book in catalog:
            if book["id"] == book_id:
                new_quantity = book["quantity"] + quantity_change
                if new_quantity < 0:
                    return False, f"Cannot reduce stock below 0. Current: {book['quantity']}, Requested change: {quantity_change}"
                
                old_quantity = book["quantity"]
                book["quantity"] = new_quantity
                book_topic = book["topic"]
                CatalogService.save_catalog(catalog)
                
                sync.propagate_write('update_stock', book_id, {'quantity_change': quantity_change})
                sync.invalidate_cache(book_id, [book_topic])
                
                action = "increased" if quantity_change > 0 else "decreased"
                return True, f"Stock {action} from {old_quantity} to {new_quantity}"
        return False, "Book not found"


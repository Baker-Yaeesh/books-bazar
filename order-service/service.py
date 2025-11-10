import json
import os
import requests
from datetime import datetime
from threading import Lock

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'orders.json')
CATALOG_SERVICE_URL = os.getenv('CATALOG_SERVICE_URL', 'http://catalog-service:8080')
data_lock = Lock()


class OrderService:
    @staticmethod
    def load_orders():
        with data_lock:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    
    @staticmethod
    def save_orders(orders):
        with data_lock:
            with open(DATA_FILE, 'w') as f:
                json.dump(orders, f, indent=2)
    
    @staticmethod
    def process_purchase(book_id):
        try:
            decrement_response = requests.post(
                f'{CATALOG_SERVICE_URL}/decrement/{book_id}',
                timeout=5
            )
            
            if decrement_response.status_code == 200:
                info_response = requests.get(
                    f'{CATALOG_SERVICE_URL}/info/{book_id}',
                    timeout=5
                )
                
                if info_response.status_code == 200:
                    book_data = info_response.json().get('data', {})
                    book_title = book_data.get('title', 'Unknown')
                else:
                    book_title = 'Unknown'
                
                orders = OrderService.load_orders()
                order = {
                    "order_id": len(orders) + 1,
                    "book_id": book_id,
                    "book_title": book_title,
                    "timestamp": datetime.now().isoformat()
                }
                orders.append(order)
                OrderService.save_orders(orders)
                
                return True, f"bought book {book_title}", 200
            
            elif decrement_response.status_code == 400:
                return False, "Book out of stock", 400
            
            elif decrement_response.status_code == 404:
                return False, "Book not found", 404
            
            else:
                return False, "Failed to process order", 500
        
        except requests.exceptions.RequestException as e:
            return False, f"Service communication error: {str(e)}", 503

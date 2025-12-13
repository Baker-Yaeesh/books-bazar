import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_sync(service_class, operation, book_id, data):
    try:
        catalog = service_class.load_catalog()
        
        if operation == 'decrement':
            for book in catalog:
                if book["id"] == book_id:
                    book["quantity"] = data['quantity']
                    service_class.save_catalog(catalog)
                    logger.info(f"Synced decrement for book {book_id}, new quantity: {data['quantity']}")
                    return True, "Sync successful"
            return False, "Book not found"
        
        elif operation == 'update_price':
            for book in catalog:
                if book["id"] == book_id:
                    book["price"] = data['price']
                    service_class.save_catalog(catalog)
                    logger.info(f"Synced price update for book {book_id}, new price: {data['price']}")
                    return True, "Sync successful"
            return False, "Book not found"
        
        elif operation == 'update_stock':
            for book in catalog:
                if book["id"] == book_id:
                    book["quantity"] += data['quantity_change']
                    service_class.save_catalog(catalog)
                    logger.info(f"Synced stock update for book {book_id}, change: {data['quantity_change']}")
                    return True, "Sync successful"
            return False, "Book not found"
        
        else:
            logger.error(f"Unknown operation: {operation}")
            return False, f"Unknown operation: {operation}"
    
    except Exception as e:
        logger.error(f"Error applying sync: {str(e)}")
        return False, f"Sync error: {str(e)}"

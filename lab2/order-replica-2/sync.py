import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_sync(service_class, order_data):
    try:
        orders = service_class.load_orders()
        
        order_id = order_data.get('order_id')
        for existing_order in orders:
            if existing_order.get('order_id') == order_id:
                logger.info(f"Order {order_id} already exists, skipping")
                return True, "Order already synced"
        
        orders.append(order_data)
        service_class.save_orders(orders)
        logger.info(f"Synced order {order_id}")
        return True, "Sync successful"
    
    except Exception as e:
        logger.error(f"Error applying sync: {str(e)}")
        return False, f"Sync error: {str(e)}"

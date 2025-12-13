import requests
import logging
import os
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPLICA_2_URL = os.getenv('ORDER_REPLICA_2_URL', 'http://order-replica-2:8083')
MAX_RETRIES = 3
RETRY_DELAY = 0.5


def propagate_order(order_data):
    payload = {
        'order': order_data
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Propagating order {order_data.get('order_id')} to replica-2 (attempt {attempt + 1})")
            response = requests.post(
                f'{REPLICA_2_URL}/sync',
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully propagated order {order_data.get('order_id')}")
                return True
            else:
                logger.warning(f"Replica-2 returned status {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to propagate to replica-2: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            sleep(RETRY_DELAY * (2 ** attempt))
    
    logger.error(f"Failed to propagate order {order_data.get('order_id')} after {MAX_RETRIES} attempts")
    return False

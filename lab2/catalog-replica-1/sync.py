import requests
import logging
import os
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPLICA_2_URL = os.getenv('CATALOG_REPLICA_2_URL', 'http://catalog-replica-2:8082')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://frontend-service:80')
MAX_RETRIES = 3
RETRY_DELAY = 0.5


def propagate_write(operation, book_id, data):
    payload = {
        'operation': operation,
        'book_id': book_id,
        'data': data
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Propagating {operation} for book {book_id} to replica-2 (attempt {attempt + 1})")
            response = requests.post(
                f'{REPLICA_2_URL}/sync',
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully propagated {operation} for book {book_id}")
                return True
            else:
                logger.warning(f"Replica-2 returned status {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to propagate to replica-2: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:
            sleep(RETRY_DELAY * (2 ** attempt))
    
    logger.error(f"Failed to propagate {operation} for book {book_id} after {MAX_RETRIES} attempts")
    return False


def invalidate_cache(book_id, topics=None):
    payload = {
        'book_id': book_id,
        'topics': topics or []
    }
    
    try:
        logger.info(f"Sending cache invalidation for book {book_id}, topics: {topics}")
        response = requests.post(
            f'{FRONTEND_URL}/invalidate-cache',
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully invalidated cache for book {book_id}")
            return True
        else:
            logger.warning(f"Frontend returned status {response.status_code} for cache invalidation")
            return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to invalidate cache: {str(e)}")
        return False

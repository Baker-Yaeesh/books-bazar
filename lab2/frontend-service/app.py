from flask import Flask, jsonify, request
import requests
import os
from collections import OrderedDict
from threading import Lock
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG_REPLICAS = [
    os.getenv('CATALOG_REPLICA_1_URL', 'http://catalog-replica-1:8080'),
    os.getenv('CATALOG_REPLICA_2_URL', 'http://catalog-replica-2:8082')
]
ORDER_REPLICAS = [
    os.getenv('ORDER_REPLICA_1_URL', 'http://order-replica-1:8081'),
    os.getenv('ORDER_REPLICA_2_URL', 'http://order-replica-2:8083')
]

CATALOG_PRIMARY = CATALOG_REPLICAS[0]
ORDER_PRIMARY = ORDER_REPLICAS[0]

MAX_CACHE_SIZE = 100
cache = OrderedDict()
cache_lock = Lock()
cache_stats = {'hits': 0, 'misses': 0, 'invalidations': 0}

catalog_lb_index = 0
order_lb_index = 0
lb_lock = Lock()


def get_next_catalog_replica():
    global catalog_lb_index
    with lb_lock:
        replica = CATALOG_REPLICAS[catalog_lb_index]
        catalog_lb_index = (catalog_lb_index + 1) % len(CATALOG_REPLICAS)
        logger.info(f"Load balancer selected catalog replica: {replica}")
        return replica


def get_next_order_replica():
    global order_lb_index
    with lb_lock:
        replica = ORDER_REPLICAS[order_lb_index]
        order_lb_index = (order_lb_index + 1) % len(ORDER_REPLICAS)
        logger.info(f"Load balancer selected order replica: {replica}")
        return replica


def get_from_cache(key):
    with cache_lock:
        if key in cache:
            cache.move_to_end(key)
            cache_stats['hits'] += 1
            logger.info(f"Cache HIT for key: {key}")
            return cache[key]
        else:
            cache_stats['misses'] += 1
            logger.info(f"Cache MISS for key: {key}")
            return None


def put_in_cache(key, value):
    with cache_lock:
        if key in cache:
            cache.move_to_end(key)
        cache[key] = value
        
        if len(cache) > MAX_CACHE_SIZE:
            oldest_key = next(iter(cache))
            cache.pop(oldest_key)
            logger.info(f"Cache evicted oldest key: {oldest_key}")


def invalidate_cache_entry(key):
    with cache_lock:
        if key in cache:
            del cache[key]
            cache_stats['invalidations'] += 1
            logger.info(f"Cache invalidated key: {key}")
            return True
        return False


@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    cache_key = f"search:{topic}"
    
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return jsonify(cached_result), 200
    
    try:
        replica_url = get_next_catalog_replica()
        response = requests.get(f'{replica_url}/search/{topic}', timeout=5)
        result = response.json()
        
        if response.status_code == 200:
            put_in_cache(cache_key, result)
        
        return jsonify(result), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/info/<int:book_id>', methods=['GET'])
def info(book_id):
    cache_key = f"info:{book_id}"
    
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return jsonify(cached_result), 200
    
    try:
        replica_url = get_next_catalog_replica()
        response = requests.get(f'{replica_url}/info/{book_id}', timeout=5)
        result = response.json()
        
        if response.status_code == 200:
            put_in_cache(cache_key, result)
        
        return jsonify(result), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/buy/<int:book_id>', methods=['POST'])
def buy(book_id):
    try:
        response = requests.post(f'{ORDER_PRIMARY}/buy/{book_id}', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/update/<int:book_id>/price', methods=['PUT'])
def update_price(book_id):
    try:
        data = request.get_json()
        response = requests.put(
            f'{CATALOG_PRIMARY}/update/{book_id}/price',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/update/<int:book_id>/stock', methods=['PUT'])
def update_stock(book_id):
    try:
        data = request.get_json()
        response = requests.put(
            f'{CATALOG_PRIMARY}/update/{book_id}/stock',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/invalidate-cache', methods=['POST'])
def invalidate_cache():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Missing request body"}), 400
        
        book_id = data.get('book_id')
        topics = data.get('topics', [])
        
        invalidated_keys = []
        
        if book_id is not None:
            info_key = f"info:{book_id}"
            if invalidate_cache_entry(info_key):
                invalidated_keys.append(info_key)
        
        for topic in topics:
            search_key = f"search:{topic}"
            if invalidate_cache_entry(search_key):
                invalidated_keys.append(search_key)
        
        logger.info(f"Cache invalidation request: book_id={book_id}, topics={topics}, invalidated={invalidated_keys}")
        
        return jsonify({
            "success": True,
            "message": f"Invalidated {len(invalidated_keys)} cache entries",
            "invalidated_keys": invalidated_keys
        }), 200
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Invalidation error: {str(e)}"}), 500


@app.route('/cache-stats', methods=['GET'])
def get_cache_stats():
    with cache_lock:
        total_requests = cache_stats['hits'] + cache_stats['misses']
        hit_rate = (cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return jsonify({
            "success": True,
            "data": {
                "hits": cache_stats['hits'],
                "misses": cache_stats['misses'],
                "invalidations": cache_stats['invalidations'],
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "cache_size": len(cache),
                "max_cache_size": MAX_CACHE_SIZE
            }
        }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

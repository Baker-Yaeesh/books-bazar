"""
Comprehensive test script for Lab 2: Bazar with Replication and Caching
Tests functionality, replication, caching, and load balancing
"""
import requests
import time
import json
from collections import defaultdict

BASE_URL = "http://localhost:9000"


GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(test_name):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    print(f"{GREEN}[OK] {message}{RESET}")


def print_error(message):
    print(f"{RED}[FAIL] {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}[INFO] {message}{RESET}")


def test_search():
    
    print_test("Search Functionality")
    
    topics = ["distributed systems", "undergraduate school", "project management", "education", "nature"]
    
    for topic in topics:
        response = requests.get(f"{BASE_URL}/search/{topic}")
        if response.status_code == 200:
            data = response.json()
            books = data.get('data', [])
            print_success(f"Search '{topic}': Found {len(books)} books")
            for book in books:
                print(f"  - ID {book['id']}: {book['title']}")
        else:
            print_error(f"Search '{topic}' failed: {response.status_code}")


def test_info():
    
    print_test("Book Info Functionality")
    
    for book_id in range(1, 8):
        response = requests.get(f"{BASE_URL}/info/{book_id}")
        if response.status_code == 200:
            data = response.json()
            book_info = data.get('data', {})
            print_success(f"Book {book_id}: {book_info.get('title')} - ${book_info.get('price')} - Stock: {book_info.get('quantity')}")
        else:
            print_error(f"Info for book {book_id} failed: {response.status_code}")


def test_cache_behavior():
    
    print_test("Cache Behavior")
    

    response = requests.get(f"{BASE_URL}/cache-stats")
    initial_stats = response.json().get('data', {})
    print_info(f"Initial cache stats: {initial_stats}")
    

    print_info("Making first search request for 'distributed systems'...")
    requests.get(f"{BASE_URL}/search/distributed systems")
    

    response = requests.get(f"{BASE_URL}/cache-stats")
    stats_after_first = response.json().get('data', {})
    print_info(f"Stats after first request: Hits={stats_after_first['hits']}, Misses={stats_after_first['misses']}")
    

    print_info("Making second search request for 'distributed systems'...")
    requests.get(f"{BASE_URL}/search/distributed systems")
    

    response = requests.get(f"{BASE_URL}/cache-stats")
    stats_after_second = response.json().get('data', {})
    print_info(f"Stats after second request: Hits={stats_after_second['hits']}, Misses={stats_after_second['misses']}")
    
    if stats_after_second['hits'] > stats_after_first['hits']:
        print_success("Cache hit detected on second request!")
    else:
        print_error("Cache hit not detected")
    
    print_info(f"Cache hit rate: {stats_after_second['hit_rate_percent']}%")


def test_purchase_and_invalidation():
    
    print_test("Purchase and Cache Invalidation")
    
    book_id = 3  # Book with stock
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    initial_stock = response.json().get('data', {}).get('quantity')
    print_info(f"Initial stock for book {book_id}: {initial_stock}")
    

    requests.get(f"{BASE_URL}/info/{book_id}")
    print_info("Cached book info")
    

    print_info(f"Purchasing book {book_id}...")
    response = requests.post(f"{BASE_URL}/buy/{book_id}")
    if response.status_code == 200:
        print_success(f"Purchase successful: {response.json().get('message')}")
    else:
        print_error(f"Purchase failed: {response.json().get('message')}")
    

    time.sleep(1)
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    new_stock = response.json().get('data', {}).get('quantity')
    print_info(f"New stock for book {book_id}: {new_stock}")
    
    if new_stock == initial_stock - 1:
        print_success("Stock correctly decremented and cache invalidated!")
    else:
        print_error(f"Stock mismatch: expected {initial_stock - 1}, got {new_stock}")


def test_stock_update():
    
    print_test("Stock Update and Cache Invalidation")
    
    book_id = 5
    quantity_change = 5
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    initial_stock = response.json().get('data', {}).get('quantity')
    print_info(f"Initial stock for book {book_id}: {initial_stock}")
    

    print_info(f"Updating stock by {quantity_change}...")
    response = requests.put(
        f"{BASE_URL}/update/{book_id}/stock",
        json={"quantity_change": quantity_change},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print_success(f"Stock update successful: {response.json().get('message')}")
    else:
        print_error(f"Stock update failed: {response.json().get('message')}")
    

    time.sleep(1)
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    new_stock = response.json().get('data', {}).get('quantity')
    print_info(f"New stock for book {book_id}: {new_stock}")
    
    if new_stock == initial_stock + quantity_change:
        print_success("Stock correctly updated and cache invalidated!")
    else:
        print_error(f"Stock mismatch: expected {initial_stock + quantity_change}, got {new_stock}")


def test_price_update():
    
    print_test("Price Update and Cache Invalidation")
    
    book_id = 6
    new_price = 65
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    initial_price = response.json().get('data', {}).get('price')
    print_info(f"Initial price for book {book_id}: ${initial_price}")
    

    print_info(f"Updating price to ${new_price}...")
    response = requests.put(
        f"{BASE_URL}/update/{book_id}/price",
        json={"price": new_price},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print_success(f"Price update successful: {response.json().get('message')}")
    else:
        print_error(f"Price update failed: {response.json().get('message')}")
    

    time.sleep(1)
    

    response = requests.get(f"{BASE_URL}/info/{book_id}")
    current_price = response.json().get('data', {}).get('price')
    print_info(f"New price for book {book_id}: ${current_price}")
    
    if current_price == new_price:
        print_success("Price correctly updated and cache invalidated!")
    else:
        print_error(f"Price mismatch: expected ${new_price}, got ${current_price}")


def test_load_balancing():
    
    print_test("Load Balancing")
    
    print_info("Making 10 search requests to test load balancing...")
    for i in range(10):
        response = requests.get(f"{BASE_URL}/search/distributed systems")
        if response.status_code == 200:
            print(f"  Request {i+1}: Success")
        else:
            print(f"  Request {i+1}: Failed")
    
    print_success("Check Docker logs to verify requests distributed across replicas")
    print_info("Run: docker-compose logs frontend-service | grep 'Load balancer'")


def test_final_cache_stats():
    
    print_test("Final Cache Statistics")
    
    response = requests.get(f"{BASE_URL}/cache-stats")
    if response.status_code == 200:
        stats = response.json().get('data', {})
        print_success("Cache Statistics:")
        print(f"  Total Requests: {stats['total_requests']}")
        print(f"  Cache Hits: {stats['hits']}")
        print(f"  Cache Misses: {stats['misses']}")
        print(f"  Cache Invalidations: {stats['invalidations']}")
        print(f"  Hit Rate: {stats['hit_rate_percent']}%")
        print(f"  Current Cache Size: {stats['cache_size']}/{stats['max_cache_size']}")
    else:
        print_error("Failed to get cache stats")


def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Lab 2: Bazar with Replication and Caching - Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    try:

        test_search()
        test_info()
        

        test_cache_behavior()
        

        test_purchase_and_invalidation()
        test_stock_update()
        test_price_update()
        

        test_load_balancing()
        

        test_final_cache_stats()
        
        print(f"\n{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}All tests completed!{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to the service. Make sure Docker containers are running:")
        print_info("Run: cd lab2 && docker-compose up")
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")


if __name__ == "__main__":
    main()

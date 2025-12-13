"""
Performance measurement script for Lab 2
Measures response times, cache performance, and replication overhead
"""
import requests
import time
import statistics
import csv
from datetime import datetime

BASE_URL = "http://localhost:9000"

def measure_response_time(func, iterations=50):
    
    times = []
    for _ in range(iterations):
        start = time.time()
        func()
        end = time.time()
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    return {
        'avg': statistics.mean(times),
        'min': min(times),
        'max': max(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }


def test_cold_cache_search():
    

    topics = ["distributed systems", "undergraduate school", "project management", "education", "nature"]
    topic = topics[int(time.time()) % len(topics)]
    requests.get(f"{BASE_URL}/search/{topic}")


def test_warm_cache_search():
    
    requests.get(f"{BASE_URL}/search/distributed systems")


def test_cold_cache_info():
    
    book_id = (int(time.time()) % 7) + 1
    requests.get(f"{BASE_URL}/info/{book_id}")


def test_warm_cache_info():
    
    requests.get(f"{BASE_URL}/info/1")


def test_purchase():
    

    requests.post(f"{BASE_URL}/buy/3")


def main():
    print("="*60)
    print("Lab 2 Performance Measurement")
    print("="*60)
    
    results = []
    

    print("\nWarming up cache...")
    for _ in range(10):
        requests.get(f"{BASE_URL}/search/distributed systems")
        requests.get(f"{BASE_URL}/info/1")
    

    print("\n1. Testing search with cold cache (50 iterations)...")
    cold_search = measure_response_time(test_cold_cache_search, 50)
    print(f"   Average: {cold_search['avg']:.2f} ms")
    results.append(["Search (Cold Cache)", cold_search['avg'], cold_search['min'], 
                    cold_search['max'], cold_search['median'], cold_search['stdev']])
    

    print("\n2. Testing search with warm cache (50 iterations)...")
    warm_search = measure_response_time(test_warm_cache_search, 50)
    print(f"   Average: {warm_search['avg']:.2f} ms")
    results.append(["Search (Warm Cache)", warm_search['avg'], warm_search['min'], 
                    warm_search['max'], warm_search['median'], warm_search['stdev']])
    

    print("\n3. Testing info with cold cache (50 iterations)...")
    cold_info = measure_response_time(test_cold_cache_info, 50)
    print(f"   Average: {cold_info['avg']:.2f} ms")
    results.append(["Info (Cold Cache)", cold_info['avg'], cold_info['min'], 
                    cold_info['max'], cold_info['median'], cold_info['stdev']])
    

    print("\n4. Testing info with warm cache (50 iterations)...")
    warm_info = measure_response_time(test_warm_cache_info, 50)
    print(f"   Average: {warm_info['avg']:.2f} ms")
    results.append(["Info (Warm Cache)", warm_info['avg'], warm_info['min'], 
                    warm_info['max'], warm_info['median'], warm_info['stdev']])
    

    print("\n5. Testing purchase operation (20 iterations)...")
    purchase = measure_response_time(test_purchase, 20)
    print(f"   Average: {purchase['avg']:.2f} ms")
    results.append(["Purchase (Write)", purchase['avg'], purchase['min'], 
                    purchase['max'], purchase['median'], purchase['stdev']])
    

    print("\n6. Getting cache statistics...")
    response = requests.get(f"{BASE_URL}/cache-stats")
    cache_stats = response.json().get('data', {})
    

    print("\n" + "="*60)
    print("Performance Summary")
    print("="*60)
    
    search_improvement = ((cold_search['avg'] - warm_search['avg']) / cold_search['avg']) * 100
    info_improvement = ((cold_info['avg'] - warm_info['avg']) / cold_info['avg']) * 100
    
    print(f"\nCache Performance:")
    print(f"  Search improvement: {search_improvement:.1f}% faster with cache")
    print(f"  Info improvement: {info_improvement:.1f}% faster with cache")
    print(f"  Cache hit rate: {cache_stats.get('hit_rate_percent', 0):.1f}%")
    print(f"  Total cache hits: {cache_stats.get('hits', 0)}")
    print(f"  Total cache misses: {cache_stats.get('misses', 0)}")
    print(f"  Cache invalidations: {cache_stats.get('invalidations', 0)}")
    

    csv_file = 'docs/performance_results.csv'
    print(f"\nSaving results to {csv_file}...")
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Operation', 'Avg (ms)', 'Min (ms)', 'Max (ms)', 'Median (ms)', 'StdDev (ms)'])
        writer.writerows(results)
        writer.writerow([])
        writer.writerow(['Cache Statistics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Hit Rate (%)', cache_stats.get('hit_rate_percent', 0)])
        writer.writerow(['Total Hits', cache_stats.get('hits', 0)])
        writer.writerow(['Total Misses', cache_stats.get('misses', 0)])
        writer.writerow(['Invalidations', cache_stats.get('invalidations', 0)])
        writer.writerow(['Search Improvement (%)', f"{search_improvement:.1f}"])
        writer.writerow(['Info Improvement (%)', f"{info_improvement:.1f}"])
    
    print(f"Results saved successfully!")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to the service.")
        print("Make sure Docker containers are running: cd lab2 && docker-compose up")
    except Exception as e:
        print(f"ERROR: {str(e)}")

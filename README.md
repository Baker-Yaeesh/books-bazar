# Books Bazar - Distributed Systems Labs

This repository contains the implementation of **Books Bazar**, a microservices-based online bookstore application. The project is divided into two phases: **Lab 1** (Basic Microservices) and **Lab 2** (Advanced Distributed Systems concepts including Replication, Caching, and Load Balancing).

## Authors
**Bakr Yaish & Hamza Younes**

---

## 🏗️ Project Architecture Overview

The system simulates an e-commerce platform where users can:
-   **Search** for books by topic.
-   **View** detailed information about a book.
-   **Purchase** books (updating stock).

The core components are:
1.  **Frontend Service**: Acts as a gateway/proxy for client requests.
2.  **Catalog Service**: Manages the book database (Id, Title, Topic, Price, Stock).
3.  **Order Service**: Handles purchase transactions.

---

## 📁 Lab 1: Basic Microservices

In this phase, the system consists of three single-instance microservices.

### 🔌 Services & Ports

| Service | Host Port | Internal Port | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | `9000` | `80` | Entry point for all client requests. |
| **Catalog** | `9080` | `8080` | Persistent storage for book data. |
| **Order** | `9081` | `8081` | Processes orders and coordinates with Catalog. |

### 📜 API Reference (Lab 1)

#### Frontend Endpoints (Public)
These are accessible via `http://localhost:9000`.

*   **Search Books**
    *   `GET /search/<topic>`
    *   Returns a list of books matching the given topic.
*   **Get Book Info**
    *   `GET /info/<item_number>`
    *   Returns details (title, price, stock) for a specific book ID.
*   **Buy Book**
    *   `POST /buy/<item_number>`
    *   Attempts to purchase a book. Returns success if stock > 0.
*   **Update Price (Admin)**
    *   `PUT /update/<item_number>/price`
    *   Body: `{"price": 15.99}`
*   **Update Stock (Admin)**
    *   `PUT /update/<item_number>/stock`
    *   Body: `{"quantity_change": 10}`

### 🚀 Running Lab 1

1.  Navigate to the `lab1` directory:
    ```bash
    cd lab1
    ```
2.  Start the system:
    ```bash
    docker-compose up --build
    ```

---

## 📁 Lab 2: Replication, Caching & Load Balancing

This phase introduces distributed systems features to improve performance, scalability, and fault tolerance.

### 🌟 Key Features

1.  **Primary-Backup Replication**:
    *   **Catalog Service**: Two replicas. Replica 1 is **Primary** (handles Writes & Reads), Replica 2 is **Backup** (handles Reads).
    *   **Order Service**: Two replicas for fault tolerance.
2.  **Load Balancing**:
    *   The **Frontend Service** acts as a software load balancer.
    *   **Read Requests** (`search`, `info`) are distributed using a **Round-Robin** algorithm between Catalog Replica 1 and Replica 2.
    *   **Write Requests** (`buy`, `update`) are always routed to the **Primary** nodes to ensure consistency.
3.  **In-Memory Caching**:
    *   Implemented in the Frontend Service using an LRU (Least Recently Used) strategy.
    *   **Max Size**: 100 items.
    *   **Cache Invalidation**: When data is updated (price/stock change), the Catalog Service notifies the Frontend to invalidate relevant cache entries.

### 🔌 Service Configuration

| Service | Host Port | Role |
| :--- | :--- | :--- |
| **Frontend** | `9000` | Load Balancer & Cache |
| **Catalog Replica 1** | `9080` | Primary (Read/Write) |
| **Catalog Replica 2** | `9082` | Backup (Read Only) |
| **Order Replica 1** | `9081` | Primary |
| **Order Replica 2** | `9083` | Backup |

### � API Reference (Lab 2)

In addition to the standard endpoints from Lab 1, Lab 2 introduces introspection endpoints:

*   **Get Cache Statistics**
    *   `GET /cache-stats`
    *   Returns JSON with `hits`, `misses`, `hit_rate`, and current `cache_size`.
*   **Invalidate Cache (Internal)**
    *   `POST /invalidate-cache`
    *   Used by backend services to clear specific cache keys after updates.

### 🧪 Testing & Verification

We have provided Python scripts to verify the system's correctness and performance.

1.  **System Verification**:
    *   Run `python test_system.py`
    *   Verifies that search, info, and buy operations work correctly.
    *   Checks if cache invalidation works after a price update.

2.  **Performance Test**:
    *   Run `python test_performance.py`
    *   Sends a burst of traffic to valid load balancing.
    *   Measures latency differences between cached and non-cached requests.

### 🚀 Running Lab 2

1.  Navigate to the `lab2` directory:
    ```bash
    cd lab2
    ```
2.  Start the distributed system:
    ```bash
    docker-compose up --build
    ```

---

## 🛠️ Prerequisites

*   **Docker Desktop** (Engine & Compose)
*   **Python 3.8+** (for running test scripts locally)
    *   Install dependencies: `pip install requests`

---

## 📝 Design Notes

*   **Consistency Model**: We use a Primary-Backup model. All writes go to the primary node, which then propagates changes to the backup. This ensures strong consistency for writes, while read replicas may be eventually consistent (though in this local network simulation, lag is negligible).
*   **Concurrency**: Thread locks (`threading.Lock`) are used in the Frontend to ensure thread safety for the shared cache and load balancer indices.

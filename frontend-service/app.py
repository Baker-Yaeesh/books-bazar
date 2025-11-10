from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Mock data for books catalog
books_catalog = {
    1: {
        "id": 1,
        "title": "Distributed Systems",
        "topic": "distributed systems",
        "price": 45.99,
        "stock": 10
    },
    2: {
        "id": 2,
        "title": "Advanced Algorithms",
        "topic": "algorithms",
        "price": 39.99,
        "stock": 5
    },
    3: {
        "id": 3,
        "title": "Machine Learning Fundamentals",
        "topic": "machine learning",
        "price": 52.99,
        "stock": 8
    },
    4: {
        "id": 4,
        "title": "Database Design",
        "topic": "databases",
        "price": 41.99,
        "stock": 12
    }
}

# Mock orders storage
orders = []
order_id_counter = 1


@app.route('/', methods=['GET'])
def home():
    """Welcome endpoint"""
    return jsonify({
        "message": "Welcome to the Book Store Frontend Service",
        "available_endpoints": [
            "/search/<topic>",
            "/info/<book_id>",
            "/buy/<book_id>",
            "/update/<book_id>/price",
            "/update/<book_id>/stock"
        ]
    })


@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    """Search for books by topic"""
    matching_books = []
    for book in books_catalog.values():
        if topic.lower() in book['topic'].lower():
            matching_books.append(book)
    
    if matching_books:
        return jsonify({
            "success": True,
            "books": matching_books,
            "count": len(matching_books)
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": f"No books found for topic: {topic}"
        }), 404


@app.route('/info/<int:book_id>', methods=['GET'])
def info(book_id):
    """Get information about a specific book"""
    if book_id in books_catalog:
        return jsonify({
            "success": True,
            "book": books_catalog[book_id]
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": f"Book with ID {book_id} not found"
        }), 404


@app.route('/buy/<int:book_id>', methods=['POST'])
def buy(book_id):
    """Purchase a book"""
    global order_id_counter
    
    if book_id not in books_catalog:
        return jsonify({
            "success": False,
            "message": f"Book with ID {book_id} not found"
        }), 404
    
    book = books_catalog[book_id]
    
    if book['stock'] <= 0:
        return jsonify({
            "success": False,
            "message": f"Book '{book['title']}' is out of stock"
        }), 400
    
    # Reduce stock
    books_catalog[book_id]['stock'] -= 1
    
    # Create order
    order = {
        "order_id": order_id_counter,
        "book_id": book_id,
        "title": book['title'],
        "price": book['price'],
        "timestamp": "2024-01-01T00:00:00Z"  # Mock timestamp
    }
    orders.append(order)
    order_id_counter += 1
    
    return jsonify({
        "success": True,
        "message": f"Successfully purchased '{book['title']}'",
        "order": order
    }), 200


@app.route('/update/<int:book_id>/price', methods=['PUT'])
def update_price(book_id):
    """Admin endpoint: Update book price"""
    if book_id not in books_catalog:
        return jsonify({
            "success": False,
            "message": f"Book with ID {book_id} not found"
        }), 404
    
    data = request.get_json()
    if not data or 'price' not in data:
        return jsonify({
            "success": False,
            "message": "Price is required"
        }), 400
    
    try:
        new_price = float(data['price'])
        if new_price < 0:
            raise ValueError("Price cannot be negative")
        
        old_price = books_catalog[book_id]['price']
        books_catalog[book_id]['price'] = new_price
        
        return jsonify({
            "success": True,
            "message": f"Price updated from ${old_price} to ${new_price}",
            "book": books_catalog[book_id]
        }), 200
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid price value"
        }), 400


@app.route('/update/<int:book_id>/stock', methods=['PUT'])
def update_stock(book_id):
    """Admin endpoint: Update book stock"""
    if book_id not in books_catalog:
        return jsonify({
            "success": False,
            "message": f"Book with ID {book_id} not found"
        }), 404
    
    data = request.get_json()
    if not data or 'stock' not in data:
        return jsonify({
            "success": False,
            "message": "Stock quantity is required"
        }), 400
    
    try:
        new_stock = int(data['stock'])
        if new_stock < 0:
            raise ValueError("Stock cannot be negative")
        
        old_stock = books_catalog[book_id]['stock']
        books_catalog[book_id]['stock'] = new_stock
        
        return jsonify({
            "success": True,
            "message": f"Stock updated from {old_stock} to {new_stock}",
            "book": books_catalog[book_id]
        }), 200
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid stock value"
        }), 400


@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    return jsonify({
        "success": True,
        "orders": orders,
        "count": len(orders)
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

from flask import Flask, jsonify, request
from service import CatalogService

app = Flask(__name__)


@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    results = CatalogService.search_by_topic(topic)
    return jsonify({"success": True, "data": results}), 200


@app.route('/info/<int:book_id>', methods=['GET'])
def info(book_id):
    book_info = CatalogService.get_book_info(book_id)
    if book_info:
        return jsonify({"success": True, "data": book_info}), 200
    else:
        return jsonify({"success": False, "message": "Book not found"}), 404


@app.route('/decrement/<int:book_id>', methods=['POST'])
def decrement(book_id):
    success, message = CatalogService.decrement_quantity(book_id)
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        if "not found" in message:
            return jsonify({"success": False, "message": message}), 404
        else:
            return jsonify({"success": False, "message": message}), 400


@app.route('/update/<int:book_id>/price', methods=['PUT'])
def update_price(book_id):
    try:
        data = request.get_json()
        if not data or 'price' not in data:
            return jsonify({"success": False, "message": "Missing 'price' field in request body"}), 400
        
        new_price = data['price']
        if not isinstance(new_price, (int, float)):
            return jsonify({"success": False, "message": "Price must be a number"}), 400
        
        success, message = CatalogService.update_price(book_id, new_price)
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            if "not found" in message:
                return jsonify({"success": False, "message": message}), 404
            else:
                return jsonify({"success": False, "message": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Invalid request: {str(e)}"}), 400


@app.route('/update/<int:book_id>/stock', methods=['PUT'])
def update_stock(book_id):
    try:
        data = request.get_json()
        if not data or 'quantity_change' not in data:
            return jsonify({"success": False, "message": "Missing 'quantity_change' field in request body"}), 400
        
        quantity_change = data['quantity_change']
        if not isinstance(quantity_change, int):
            return jsonify({"success": False, "message": "Quantity change must be an integer"}), 400
        
        success, message = CatalogService.update_stock(book_id, quantity_change)
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            if "not found" in message:
                return jsonify({"success": False, "message": message}), 404
            else:
                return jsonify({"success": False, "message": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Invalid request: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

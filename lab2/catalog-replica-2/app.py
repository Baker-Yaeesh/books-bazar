from flask import Flask, jsonify, request
from service import CatalogService
import sync

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


@app.route('/sync', methods=['POST'])
def sync_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Missing request body"}), 400
        
        operation = data.get('operation')
        book_id = data.get('book_id')
        op_data = data.get('data')
        
        if not all([operation, book_id is not None, op_data]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        success, message = sync.apply_sync(CatalogService, operation, book_id, op_data)
        
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Sync error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)


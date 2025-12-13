from flask import Flask, jsonify, request
from service import OrderService
import sync

app = Flask(__name__)


@app.route('/sync', methods=['POST'])
def sync_endpoint():
    try:
        data = request.get_json()
        if not data or 'order' not in data:
            return jsonify({"success": False, "message": "Missing order data"}), 400
        
        order_data = data['order']
        success, message = sync.apply_sync(OrderService, order_data)
        
        if success:
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 400
    
    except Exception as e:
        return jsonify({"success": False, "message": f"Sync error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)

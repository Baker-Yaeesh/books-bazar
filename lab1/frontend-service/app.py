from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

CATALOG_SERVICE_URL = os.getenv('CATALOG_SERVICE_URL', 'http://catalog-service:8080')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:8081')


@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    try:
        response = requests.get(f'{CATALOG_SERVICE_URL}/search/{topic}', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/info/<int:book_id>', methods=['GET'])
def info(book_id):
    try:
        response = requests.get(f'{CATALOG_SERVICE_URL}/info/{book_id}', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/buy/<int:book_id>', methods=['POST'])
def buy(book_id):
    try:
        response = requests.post(f'{ORDER_SERVICE_URL}/buy/{book_id}', timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/update/<int:book_id>/price', methods=['PUT'])
def update_price(book_id):
    """Admin endpoint: Update book price"""
    try:
        data = request.get_json()
        response = requests.put(
            f'{CATALOG_SERVICE_URL}/update/{book_id}/price',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


@app.route('/update/<int:book_id>/stock', methods=['PUT'])
def update_stock(book_id):
    """Admin endpoint: Update book stock"""
    try:
        data = request.get_json()
        response = requests.put(
            f'{CATALOG_SERVICE_URL}/update/{book_id}/stock',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "message": f"Service unavailable: {str(e)}"}), 503


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

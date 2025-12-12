from flask import Flask, jsonify
from service import OrderService

app = Flask(__name__)


@app.route('/buy/<int:book_id>', methods=['POST'])
def buy(book_id):
    success, message, status_code = OrderService.process_purchase(book_id)
    if success:
        return jsonify({"success": True, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message}), status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)

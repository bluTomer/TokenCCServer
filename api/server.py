# server.py

import os
import uuid
from flask import Flask, request, jsonify, abort
from flask_redis import FlaskRedis
from luhn import verify

app = Flask(__name__)
app.config['REDIS_URL'] = os.getenv('REDIS_URL')
redis_client = FlaskRedis(app)

@app.route('/creditcard', methods=['POST'])
def add_creditcard():
    '''
    Add a credit card number to the system.
    Returns a token associated with the credit card number.
    '''
    if not request.json or not 'credit-card' in request.json:
        abort(400)

    cc = request.json['credit-card']
    ccnum = ''.join(filter(str.isdigit, cc))
    if not verify(ccnum):
        abort(400)

    token = str(uuid.uuid4())
    result = redis_client.set(token, cc)
    return jsonify({ 'token': token }), 200

@app.route('/creditcard/<id>', methods=['GET'])
def get_creditcard(id):
    '''
    Get a creditcard number associated with the given token.
    '''
    ccbytes = redis_client.get(id)
    if not ccbytes:
        abort(404)

    return jsonify({ 'credit-card': ccbytes.decode() }), 200

@app.route('/creditcard/<id>', methods=['DELETE'])
def delete_creditcard(id):
    '''
    Remove a creditcard number associated with the given token.
    '''
    deleteResponse = redis_client.delete(id)
    if not deleteResponse:
        abort(404)

    return '', 204
    
if __name__ == '__main__':
    app.run()

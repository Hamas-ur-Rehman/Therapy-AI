"""
This file generates the API and initializes the class Therapy
"""

from GPT import chat
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def index():
    QUERY = request.json.get('query')
    USER_ID = request.json.get('user_id')
    result = chat(QUERY, USER_ID)
    
    response = {'response': result, 'query':QUERY,'status': 'success'}
    return jsonify(response)

if __name__ == '__main__':
    app.run()

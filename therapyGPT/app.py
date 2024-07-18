"""
This file generates the API and initializes the class Therapy
"""

from GPT import *
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil

def delete_folder(folder_path,USER_ID):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        return  f'{USER_ID} chats deleted with success','success'
    else:
        return  f'Failed to Delete {USER_ID} chats','failed'

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def index():
    QUERY = request.json.get('query')
    USER_ID = request.json.get('user_id')
    result = chat(QUERY, USER_ID)
    
    response = {'response': result, 'query':QUERY,'status': 'success'}
    return jsonify(response)

@app.route('/delete', methods=['DELETE'])
def delete():
    USER_ID = request.json.get('user_id')
    
    message,status = delete_folder(f'./{USER_ID}',USER_ID)
    response = {'message':message, 'status': status}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

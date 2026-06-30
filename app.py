import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "message": "Sapat App Backend engine is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
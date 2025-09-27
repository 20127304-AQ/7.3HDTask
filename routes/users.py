from flask import Blueprint, request, jsonify
from models import users

users_bp = Blueprint('users', __name__)

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = next((u for u in users if u['username'] == data['username'] and u['password'] == data['password']), None)
    if user:
        return jsonify(token="mysecrettoken")
    return jsonify({"message": "Invalid credentials"}), 401

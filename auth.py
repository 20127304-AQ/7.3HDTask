from flask import request, jsonify
from functools import wraps
from models import users

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != "Bearer mysecrettoken":
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

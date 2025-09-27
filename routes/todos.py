from flask import Blueprint, request, jsonify
from functools import wraps

todos_bp = Blueprint('todos', __name__)

# In-memory storage
TODOS = {}
NEXT_ID = 1

# Dummy token auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != "Bearer mysecrettoken":
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@todos_bp.route('/', methods=['POST'])
@token_required
def add_todo():
    global NEXT_ID
    data = request.get_json()
    todo = {"id": NEXT_ID, "task": data["task"]}
    TODOS[NEXT_ID] = todo
    NEXT_ID += 1
    return jsonify(todo), 201

@todos_bp.route('/', methods=['GET'])
@token_required
def get_todos():
    return jsonify(list(TODOS.values())), 200

@todos_bp.route('/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(todo_id):
    data = request.get_json()
    if todo_id not in TODOS:
        return jsonify({"message": "Not found"}), 404
    TODOS[todo_id]["task"] = data["task"]
    return jsonify(TODOS[todo_id]), 200

@todos_bp.route('/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(todo_id):
    if todo_id not in TODOS:
        return jsonify({"message": "Not found"}), 404
    deleted = TODOS.pop(todo_id)
    return jsonify(deleted), 200

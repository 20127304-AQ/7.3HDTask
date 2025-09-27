from flask import Blueprint, request, jsonify
from models import todos
from app import TODO_OPERATIONS
from auth import token_required

todos_bp = Blueprint('todos', __name__)

@todos_bp.route('/', methods=['GET'])
@token_required
def get_todos():
    return jsonify(todos)

@todos_bp.route('/', methods=['POST'])
@token_required
def add_todo():
    data = request.json
    todo = {"id": len(todos) + 1, "task": data["task"]}
    todos.append(todo)
    TODO_OPERATIONS.labels(operation='create').inc()
    return jsonify(todo), 201

@todos_bp.route('/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(todo_id):
    data = request.json
    for todo in todos:
        if todo["id"] == todo_id:
            todo["task"] = data["task"]
            TODO_OPERATIONS.labels(operation='update').inc()
            return jsonify(todo)
    return jsonify({"message": "Not found"}), 404

@todos_bp.route('/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    TODO_OPERATIONS.labels(operation='delete').inc()
    return jsonify({"message": "Deleted"})

from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from routes.todos import todos_bp
from routes.users import users_bp

app = Flask(__name__)

# Metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests')
TODO_OPERATIONS = Counter('todo_operations_total', 'Total TODO CRUD operations', ['operation'])

# Register blueprints
app.register_blueprint(todos_bp, url_prefix='/todos')
app.register_blueprint(users_bp, url_prefix='/users')

@app.before_request
def before_request():
    REQUESTS.inc()

@app.route('/')
def index():
    return jsonify(message="Hello from Flask TODO App!")

@app.route('/health')
def health():
    return jsonify(status="ok")

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

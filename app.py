from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from routes.todos import todos_bp  # Import blueprint

app = Flask(__name__)
REQUESTS = Counter('http_requests_total','Total HTTP requests')

@app.route('/')
def index():
    REQUESTS.inc()
    return jsonify(message="Hello from Flask TODO App!")  # updated message

@app.route('/health')
def health():
    return jsonify(status="ok")

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Register blueprint
app.register_blueprint(todos_bp, url_prefix='/todos')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

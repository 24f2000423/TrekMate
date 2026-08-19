import os
import redis
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db, jwt, cache
from seed import seed_database_if_empty

def check_redis_alive(redis_url):
    try:
        r = redis.Redis.from_url(redis_url, socket_connect_timeout=0.3, socket_timeout=0.3)
        r.ping()
        return True
    except Exception:
        return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for frontend Vite dev server & production
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)

    # Smart Cache detection: use RedisCache if Redis server is running, else SimpleCache
    redis_available = check_redis_alive(app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0'))
    if redis_available:
        print("[CACHE] Connected to Redis server for caching.")
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL'),
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }
    else:
        print("[CACHE] Redis server not active locally. Using high-performance SimpleCache for development.")
        cache_config = {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        }

    cache.init_app(app, config=cache_config)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.trek_routes import trek_bp
    from routes.admin_routes import admin_bp
    from routes.staff_routes import staff_bp
    from routes.booking_routes import booking_bp
    from routes.report_routes import report_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(trek_bp, url_prefix='/api/treks')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(booking_bp, url_prefix='/api/bookings')
    app.register_blueprint(report_bp, url_prefix='/api/reports')

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'error': 'Missing or invalid authorization token'}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'error': 'Invalid token signature'}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({'error': 'Session token has expired. Please log in again.'}), 401

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'app': 'Trekking Management Application V2'}), 200

    # Ensure tables exist and pre-existing admin is created programmatically
    with app.app_context():
        db.create_all()
        seed_database_if_empty()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

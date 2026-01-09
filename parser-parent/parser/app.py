from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
import os
# Import blueprints
from routes.ingestion import ingestion_bp
from routes.retrieval import retrieval_bp
from routes.teaching import teaching_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    db.init_app(app)
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(retrieval_bp)
    app.register_blueprint(teaching_bp)
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Upside Learning API'
        }), 200
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Upside Learning API',
            'version': '1.0.0',
            'endpoints': {
                'ingestion': '/api/ingestion',
                'retrieval': '/api/retrieval',
                'teaching': '/api/teaching'
            }
        }), 200
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=7312
    )

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db
from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_db()
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')


    @app.route('/')
    def index():
        return {
            'message': 'API Flask - Login, Cadastro e Reconhecimento Facial',
            'version': '1.0.0',
            'endpoints': {
            'auth': {
            'register': 'POST /api/auth/register',
            'login': 'POST /api/auth/login',
            'logout': 'POST /api/auth/logout'
            },
            'face': {
            'register': 'POST /api/user/face/register',
            'recognize': 'POST /api/user/face/recognize'
            }
            }
        }
    return app


import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'troque-esta-chave-em-producao'
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'app.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    FACE_ENCODING_TOLERANCE = 0.6



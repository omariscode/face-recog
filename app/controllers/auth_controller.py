from flask import Blueprint, request
from functools import wraps
from app.models.user import User
from app.views.responses import ResponseView
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return ResponseView.unauthorized('Token de autenticação não fornecido')
        if token.startswith('Bearer '):
            token = token[7:]
            user_id = AuthService.verify_token(token)
        if not user_id:
            return ResponseView.unauthorized('Token inválido ou expirado')
        request.current_user_id = user_id
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return ResponseView.error('Dados não fornecidos')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not username or not email or not password:
        return ResponseView.error('Username, email e senha são obrigatórios')
    if User.find_by_username(username):
        return ResponseView.error('Username já está em uso', 409)
    if User.find_by_email(email):
        return ResponseView.error('Email já está em uso', 409)
    password_hash = User.hash_password(password)
    user = User(username=username, email=email, password_hash=password_hash, full_name=full_name)
    user.save()
    token = AuthService.generate_token(user.id)
    return ResponseView.success( data={'user': user.to_dict(), 'token': token}, message='Usuário cadastrado com sucesso', status_code=201)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return ResponseView.error('Dados não fornecidos')
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return ResponseView.error('Username e senha são obrigatórios')
    user = User.find_by_username(username)
    if not user or not user.verify_password(password):
        return ResponseView.unauthorized('Credenciais inválidas')
    token = AuthService.generate_token(user.id)
    return ResponseView.success(data={'user': user.to_dict(), 'token': token}, message='Login realizado com sucesso')

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
 # Em uma implementação mais completa, você poderia invalidar o token
 # Por enquanto, apenas confirmamos que o usuário está autenticado
    return ResponseView.success(message='Logout realizado com sucesso')
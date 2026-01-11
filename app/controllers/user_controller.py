from flask import Blueprint, request
from app.models.user import User
from app.views.responses import ResponseView
from app.controllers.auth_controller import token_required
from app.services.face_recognition_service import FaceRecognitionService

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    user_id = request.current_user_id
    user = User.find_by_id(user_id)
    if not user:
        return ResponseView.not_found('Usuário não encontrado')
    data = user.to_dict()
    extra = user.get_user_info()
    if extra:
        data.update(extra)
    return ResponseView.success(data=data, message='Perfil recuperado com sucesso')

@user_bp.route('/info', methods=['POST', 'PUT'])
@token_required
def save_user_info():
    user_id = request.current_user_id
    user = User.find_by_id(user_id)
    if not user:
        return ResponseView.not_found('Usuário não encontrado')
    data = request.get_json()
    if not data:
        return ResponseView.error('Dados não fornecidos')
    user.save_user_info(
    phone=data.get('phone'),
    address=data.get('address'),
    birth_date=data.get('birth_date'),
    bio=data.get('bio')
    )
    return ResponseView.success(
    message='Informações salvas com sucesso',
    status_code=201 if request.method == 'POST' else 200
    )

@user_bp.route('/face/register', methods=['POST'])
@token_required
def register_face():
    user_id = request.current_user_id
    user = User.find_by_id(user_id)
    if not user:
        return ResponseView.not_found('Usuário não encontrado')
    if 'image' not in request.files:
        return ResponseView.error('Imagem não fornecida')
    file = request.files['image']
    if file.filename == '':
        return ResponseView.error('Nenhum arquivo selecionado')
    result = FaceRecognitionService.register_face(user_id, file)
    if result['success']:
        return ResponseView.success(result['data'], 'Face cadastrada com sucesso', 201)
    return ResponseView.error(result['message'])

@user_bp.route('/face/recognize', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return ResponseView.error('Imagem não fornecida')
    file = request.files['image']
    if file.filename == '':
        return ResponseView.error('Nenhum arquivo selecionado')
    result = FaceRecognitionService.recognize_face(file)
    if result['success']:
        return ResponseView.success(result['data'], 'Face reconhecida com sucesso')
    return ResponseView.error(result['message'], 404)
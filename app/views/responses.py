from flask import jsonify

class ResponseView:
    @staticmethod
    def success(data=None, message='Operação realizada com sucesso', status_code=200):
        return jsonify({'success': True, 'message': message, 'data': data}), status_code
    
    @staticmethod
    def error(message='Erro na operação', status_code=400, errors=None):
        return jsonify({'success': False, 'message': message, 'errors': errors}), status_code
    
    @staticmethod
    def unauthorized(message='Não autorizado'):
        return ResponseView.error(message, 401)
    
    @staticmethod
    def not_found(message='Recurso não encontrado'):
        return ResponseView.error(message, 404)
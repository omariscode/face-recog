import face_recognition
import numpy as np
import os
from PIL import Image
from app.config import Config
from app.extensions import db 

class FaceRecognitionService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_uploaded_file(file, user_id):
        if not FaceRecognitionService.allowed_file(file.filename):
            raise ValueError('Tipo de arquivo não permitido')
        
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        filename = f'user_{user_id}_{os.urandom(8).hex()}.jpg'
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        image = Image.open(file)
        image = image.convert('RGB')
        image.save(filepath, 'JPEG')
        return filepath
    
    @staticmethod
    def get_face_encoding(image_path):
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) == 0:
            return None
        return face_encodings[0]

    @staticmethod
    def register_face(user_id, file):
        try:
            image_path = FaceRecognitionService.save_uploaded_file(file, user_id)
            encoding = FaceRecognitionService.get_face_encoding(image_path)
            if encoding is None:
                os.remove(image_path)
                return {'success': False, 'message': 'Nenhuma face detectada na imagem'}
            conn = db.get_connection()
            cursor = conn.cursor()
            encoding_bytes = encoding.tobytes()
            cursor.execute('''
            INSERT INTO face_encodings (user_id, encoding, image_path)
            VALUES (?, ?, ?)
            ''', (user_id, encoding_bytes, image_path))
            conn.commit()
            face_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'data': {'face_id': face_id, 'image_path': image_path}}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao cadastrar face: {str(e)}'}
        
    @staticmethod
    def recognize_face(file):
        temp_name = f"temp_{os.urandom(8).hex()}.jpg"
        temp_path = os.path.join(Config.UPLOAD_FOLDER, temp_name)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        image = Image.open(file)
        image = image.convert('RGB')
        image.save(temp_path, 'JPEG')
        unknown_encoding = FaceRecognitionService.get_face_encoding(temp_path)
        os.remove(temp_path)

        if unknown_encoding is None:
            return {'success': False, 'message': 'Nenhuma face detectada na imagem'}
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT fe.id, fe.user_id, fe.encoding, u.username, u.full_name
        FROM face_encodings fe
        JOIN users u ON fe.user_id = u.id
        ''')
        faces = cursor.fetchall()
        conn.close()

        if len(faces) == 0:
            return {'success': False, 'message': 'Nenhuma face cadastrada no sistema'}
        
        for face in faces:
            known_encoding = np.frombuffer(face['encoding'], dtype=np.float64)
            distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            if distance < Config.FACE_ENCODING_TOLERANCE:
                return {
                'success': True,
                'data': {
                'user_id': face['user_id'],
                'username': face['username'],
                'full_name': face['full_name'],
                'confidence': float(1 - distance),
                'face_id': face['id']
                }
                }
            
        return {'success': False, 'message': 'Face não reconhecida'}
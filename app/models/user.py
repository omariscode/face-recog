import sqlite3
import bcrypt
from datetime import datetime
from app.extensions import db


class User:
    def __init__(self, username, email, password_hash, full_name=None, user_id=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def save(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
            ''', (self.username, self.email, self.password_hash, self.full_name))
            conn.commit()
            self.id = cursor.lastrowid
            return self
        except sqlite3.IntegrityError:
            conn.rollback()
            raise ValueError('Usuário ou email já existe')
        finally:
            conn.close()

    @staticmethod
    def find_by_username(username):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row['username'], row['email'], row['password_hash'], row['full_name'], row['id'])
        return None

    @staticmethod
    def find_by_email(email):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row['username'], row['email'], row['password_hash'], row['full_name'], row['id'])
        return None

    @staticmethod
    def find_by_id(user_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(row['username'], row['email'], row['password_hash'], row['full_name'], row['id'])
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name
        }
        
    def save_user_info(self, phone=None, address=None, birth_date=None, bio=None):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM user_info WHERE user_id = ?', (self.id,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute('''
            UPDATE user_info
            SET phone = ?, address = ?, birth_date = ?, bio = ?
            WHERE user_id = ?
            ''', (phone, address, birth_date, bio, self.id))
        else:
            cursor.execute('''
            INSERT INTO user_info (user_id, phone, address, birth_date, bio)
            VALUES (?, ?, ?, ?, ?)
            ''', (self.id, phone, address, birth_date, bio))
            conn.commit()
            conn.close()

    def get_user_info(self):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_info WHERE user_id = ?', (self.id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'phone': row['phone'],
                'address': row['address'],
                'birth_date': row['birth_date'],
                'bio': row['bio']
            }
        return None
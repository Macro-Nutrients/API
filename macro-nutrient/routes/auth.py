# # routes/auth.py
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
# from services.store_data import store_data
# from werkzeug.security import generate_password_hash, check_password_hash

# auth_bp = Blueprint('auth', __name__)

# # Simulasi database pengguna (pengganti MongoDB atau database lainnya)
# users_db = {}

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({"msg": "Username dan password diperlukan"}), 400

#     if username in users_db:
#         return jsonify({"msg": "Username sudah terdaftar"}), 400

#     hashed_password = generate_password_hash(password)
#     users_db[username] = hashed_password
#     user_id = f"user_{username}"
#     user_data = {
#         'username': username,
#         'password': hashed_password
#     }

#     # Menyimpan data ke Firestore menggunakan store_data
#     store_data('users', user_id, user_data)

#     return jsonify({"msg": "Registrasi berhasil"}), 201

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     stored_password = users_db.get(username)
#     if not stored_password or not check_password_hash(stored_password, password):
#         return jsonify({"msg": "Username atau password salah"}), 401

#     access_token = create_access_token(identity=username)
#     return jsonify(access_token=access_token), 200

# @auth_bp.route('/', methods=['GET'])
# @jwt_required()
# def index():
#     current_user = get_jwt_identity()
#     return jsonify(message=f"Selamat datang, {current_user}!")

import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from google.cloud import firestore
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)
db = firestore.Client(project="macro-nutrient")  # Pakai ADC

# Validasi email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

# Validasi password: 8+ karakter, huruf & angka/simbol
def is_valid_password(password):
    password_regex = r'^(?=.*[a-zA-Z])(?=.*[\d\W])[a-zA-Z\d\W]{8,}$'
    return re.match(password_regex, password)

# ================= REGISTER ==================
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')

        # Validasi input
        if not email or not password or not username:
            return jsonify(error=True, message="Email, username, dan password diperlukan"), 400
        if not is_valid_email(email):
            return jsonify(error=True, message="Email tidak valid"), 400
        if not is_valid_password(password):
            return jsonify(
                error=True,
                message="Password minimal 8 karakter, mengandung huruf dan angka/simbol"
            ), 400

        users_ref = db.collection('users')
        snapshot = users_ref.where('email', '==', email).get()

        if snapshot:
            return jsonify(error=True, message="Email sudah terdaftar"), 400

        hashed_pw = generate_password_hash(password)
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_pw
        }

        users_ref.add(user_data)
        return jsonify(error=False, message="Registrasi berhasil"), 201

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        return jsonify(error=True, message="Terjadi kesalahan pada server"), 500

# ================= LOGIN ==================
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify(error=True, message="Email dan password diperlukan"), 400

        users_ref = db.collection('users')
        snapshot = users_ref.where('email', '==', email).get()

        if not snapshot:
            return jsonify(error=True, message="Email atau password salah"), 401

        user_doc = snapshot[0]
        user = user_doc.to_dict()

        if not check_password_hash(user['password'], password):
            return jsonify(error=True, message="Email atau password salah"), 401

        # Tambahkan username ke token
        token = create_access_token(identity=user['username'])

        return jsonify(
            error=False,
            message="Login berhasil",
            result={
                "userId": user_doc.id,
                "username": user['username'],
                "token": token
            }
        ), 200

    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return jsonify(error=True, message="Terjadi kesalahan pada server"), 500

# ================= PROTECTED ==================
@auth_bp.route('/', methods=['GET'])
@jwt_required()
def protected_index():
    username = get_jwt_identity()
    return jsonify(message=f"Selamat datang, pengguna dengan username {username}")
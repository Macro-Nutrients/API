# from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
# from bson.objectid import ObjectId
# import bcrypt
# import jwt
# import datetime

# app = Flask(__name__)

# # Config MongoDB dan Secret Key
# app.config["MONGO_URI"] = "mongodb://localhost:27017/authdb"
# app.config["SECRET_KEY"] = "rahasia_kamu"

# mongo = PyMongo(app)
# users_collection = mongo.db.users

# # REGISTRASI
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     username = data['username']
#     password = data['password']

#     # Cek apakah username sudah ada
#     if users_collection.find_one({'username': username}):
#         return jsonify({"msg": "Username sudah terdaftar"}), 400

#     hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     user_id = users_collection.insert_one({
#         "username": username,
#         "password": hashed_pw
#     }).inserted_id

#     return jsonify({"msg": "Registrasi berhasil", "id": str(user_id)}), 201

# # LOGIN
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data['username']
#     password = data['password']

#     user = users_collection.find_one({'username': username})
#     if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
#         token = jwt.encode({
#             'user_id': str(user['_id']),
#             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
#         }, app.config['SECRET_KEY'], algorithm='HS256')

#         return jsonify({"token": token}), 200
#     return jsonify({"msg": "Username atau password salah"}), 401

# # ENDPOINT TERPROTEKSI (Contoh)
# @app.route('/protected', methods=['GET'])
# def protected():
#     token = request.headers.get('Authorization')
#     if not token:
#         return jsonify({"msg": "Token tidak ditemukan"}), 403
#     try:
#         decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#         user = users_collection.find_one({"_id": ObjectId(decoded['user_id'])})
#         return jsonify({"msg": f"Halo {user['username']}"}), 200
#     except jwt.ExpiredSignatureError:
#         return jsonify({"msg": "Token expired"}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({"msg": "Token tidak valid"}), 401

# if __name__ == '__main__':
#     app.run(debug=True)

# app.py
from flask import Flask
from routes.auth import auth_bp
from flask_jwt_extended import JWTManager
from config import Config
import firebase_admin
from google.auth import exceptions
from google.cloud import firestore

# Inisialisasi Firebase SDK (menggunakan ADC tanpa Firebase Admin SDK)
try:
    db = firestore.Client(project=Config.PROJECT_ID)  # Menggunakan ID proyek dari konfigurasi
    print("Firestore client berhasil diinisialisasi.")
except exceptions.DefaultCredentialsError as e:
    print(f"Gagal menginisialisasi Firestore: {e}")

# Inisialisasi aplikasi Flask
app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi JWT Manager
jwt = JWTManager(app)

# Mendaftarkan blueprint untuk autentikasi
app.register_blueprint(auth_bp, url_prefix="/auth")

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True)
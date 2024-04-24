from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, unset_jwt_cookies, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
import pymysql
from utils import get_connection

bp = Blueprint("auth", __name__)


# User registration endpoint
@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data['username']
        email = data['email']
        phone = data['phone']
        password = data['password']
        confirm_password = data['confirm_password']

        if len(password) < 8:
            raise Exception("Password must be at least 8 characters long")
        elif password != confirm_password:
            raise Exception("Passwords do not match")
            
        password_hash = generate_password_hash(password)

        connection = get_connection()

        cursor = connection.cursor()

        sql = 'INSERT INTO users (username, email, phone, password) VALUES (%s, %s, %s, %s)'

        cursor.execute(sql, (username, email, phone, password_hash))
        connection.commit()

        return jsonify({
            "message": "Registration successful"
        })

    except Exception as e:
        return jsonify ({
            "error": str(e)
        })

# User login endpoint
@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']

        connection = get_connection()

        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = 'SELECT password FROM users WHERE username = %s'
        cursor.execute(sql, username)
        user = cursor.fetchone()

        if user is None:
            raise Exception("Invalid login credentials")
        
        if not check_password_hash(user['password'], password):
            raise Exception("Invalid login credentials")

        access_token = create_access_token(identity=username)
        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        })

    except Exception as e:
        return jsonify ({
            "error": str(e)
        })

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        unset_jwt_cookies(response)
        
        return jsonify({"message": "Logout successful"})
    except Exception as e:
        return jsonify({"message": "Logout failed", "error": str(e)})

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight check successful'}), 200

    if request.method == 'POST':
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            is_artist = data.get('is_artist', False)

            if not username or not email or not password:
                return jsonify(message="Missing required fields"), 400

            if User.query.filter_by(username=username).first():
                return jsonify(message="Username already exists"), 400

            if User.query.filter_by(email=email).first():
                return jsonify(message="Email already exists"), 400

            user = User(username=username, email=email, is_artist=is_artist)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return jsonify(message="User registered successfully"), 201
        except Exception as e:
            current_app.logger.error(f"Error in register endpoint: {e}")
            return jsonify(message="Internal Server Error"), 500

@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight check successful'}), 200

    if request.method == 'POST':
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')

            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                access_token = create_access_token(identity=user.id)
                return jsonify(access_token=access_token), 200
            else:
                return jsonify(message="Invalid credentials"), 401
        except Exception as e:
            current_app.logger.error(f"Error in login endpoint: {e}")
            return jsonify(message="Internal Server Error"), 500

@bp.route('/profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def profile():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight check successful'}), 200

    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user)

        return jsonify({
            'username': user.username,
            'email': user.email,
            'is_artist': user.is_artist
        })
    except Exception as e:
        current_app.logger.error(f"Error in profile endpoint: {e}")
        return jsonify(message="Internal Server Error"), 500

@bp.route('/refresh', methods=['POST', 'OPTIONS'])
@jwt_required(refresh=True)
def refresh():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight check successful'}), 200

    try:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return jsonify(access_token=access_token), 200
    except Exception as e:
        current_app.logger.error(f"Error in refresh endpoint: {e}")
        return jsonify(message="Internal Server Error"), 500

@bp.route('/logout', methods=['POST', 'OPTIONS'])
@jwt_required()
def logout():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight check successful'}), 200

    return jsonify(message="Logout successful"), 200

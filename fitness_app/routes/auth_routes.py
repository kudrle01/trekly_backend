from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from fitness_app.models import User
from fitness_app.utils.bcrypt_utils import check_password, hash_password
from fitness_app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.objects(email=username.lower()).first()
    if not user:
        user = User.objects(username=username.lower()).first()

    if not user or not check_password(password, user.password):
        return error_response("Invalid username or password", 401)

    access_token = create_access_token(identity=str(user.id),
                                       expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    refresh_token = create_refresh_token(identity=str(user.id),
                                         expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    return success_response({"access_token": access_token, "refresh_token": refresh_token}, 200)


@auth_bp.route("/register", methods=['POST'])
def register():
    username = request.json.get('username').lower()
    email = request.json.get('email').lower()

    # Check if user exists using MongoEngine
    if User.objects(username=username).first():
        return error_response("Username is already used", 401)
    if User.objects(email=email).first():
        return error_response("E-mail is already used", 401)

    hashed_password = hash_password(request.json.get('password'))
    new_user = User(username=username,
                    password=hashed_password,
                    email=email,
                    birthDate=request.json.get('birthDate'),
                    gender=request.json.get('gender'),
                    ).save()

    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))
    return success_response({"access_token": access_token, "refresh_token": refresh_token}, 200)


@auth_bp.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id,
                                           expires_delta=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    new_refresh_token = create_refresh_token(identity=current_user_id,
                                             expires_delta=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    response = jsonify({
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "msg": "Tokens refreshed"
    })
    return response, 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response

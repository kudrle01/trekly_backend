from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from mongoengine import DoesNotExist
from fitness_app.models import User, Workout, Routine, Follow, WorkoutLike, WorkoutComment, Notification, \
    AchievementGained, UserReport, WorkoutReport
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

@auth_bp.route('/delete_account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)

        WorkoutLike.objects(user=user).delete()
        WorkoutComment.objects(user=user).delete()
        Notification.objects(user=user).delete()
        Notification.objects(initiator=user).delete()
        AchievementGained.objects(user=user).delete()
        Follow.objects(followed=user).delete()
        Follow.objects(follower=user).delete()
        Routine.objects(user=user).delete()
        Workout.objects(user=user).delete()
        UserReport.objects(reporter=user).delete()
        UserReport.objects(reported=user).delete()
        WorkoutReport.objects(reporter=user).delete()

        user.delete()

        response = jsonify({"msg": "User account deleted successfully."})
        unset_jwt_cookies(response)
        return response, 200
    except DoesNotExist:
        return error_response("User not found", 404)
    except Exception as e:
        current_app.logger.error(f"Error deleting user account: {str(e)}")
        return error_response("Failed to delete user account", 500)


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

from bson import ObjectId
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from fitness_app.models import User, Workout, Routine, Follow
from fitness_app.utils.responses import error_response, success_response
from fitness_app.utils.serializer import serialize_documents, serialize_doc

users_bp = Blueprint('users', __name__)


@users_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return error_response("User not found", 401)

    user_data = {
        "_id": str(user.id),
        "username": user.username,
        "birthDate": user.birthDate,
        "registrationDate": user.registrationDate,
        "profilePhotoUrl": user.profilePhotoUrl,
        "lastStreakEvidence": user.lastStreakEvidence,
        "streak": user.streak,
        "restDays": user.restDays,
        "workouts": serialize_documents(Workout.objects(user_id=ObjectId(user_id))),
        "routines": serialize_documents(Routine.objects(user_id=ObjectId(user_id))),
        "followers": serialize_documents(Follow.objects(followed=ObjectId(user_id))),
        "following": serialize_documents(Follow.objects(follower=ObjectId(user_id))),
    }
    return success_response(user_data, 200)


@users_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_profile_by_id(user_id):
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return error_response("User not found", 401)
    user_data = {
        "_id": str(user.id),
        "username": user.username,
        "birthDate": user.birthDate,
        "registrationDate": user.registrationDate,
        "profilePhotoUrl": user.profilePhotoUrl,
        "lastStreakEvidence": user.lastStreakEvidence,
        "streak": user.streak,
        "restDays": user.restDays,
        "workouts": serialize_documents(Workout.objects(user_id=ObjectId(user_id))),
        "routines": serialize_documents(Routine.objects(user_id=ObjectId(user_id))),
        "followers": serialize_documents(Follow.objects(followed=ObjectId(user_id))),
        "following": serialize_documents(Follow.objects(follower=ObjectId(user_id))),
    }
    return success_response(user_data, 200)


@users_bp.route("/all", methods=["GET"])
@jwt_required()
def fetch_users():
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    username_query = request.args.get('query', '')
    skip = (page - 1) * limit

    query = {}
    if username_query:
        query['username'] = {'$regex': username_query, '$options': 'i'}

    try:
        users_query = User.objects(__raw__=query, id__ne=ObjectId(user_id)).skip(skip).limit(limit)
        users = list(users_query)
        # Serialize users to include username and profilePhotoUrl
        user_data = [{
            "_id": str(user.id),
            "username": user.username,
            "profilePhotoUrl": user.profilePhotoUrl
        } for user in users]
        total_users = User.objects(__raw__=query, id__ne=ObjectId(user_id)).count()
        has_more = skip + limit < total_users

        return jsonify({
            'users': user_data,
            'hasMore': has_more
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

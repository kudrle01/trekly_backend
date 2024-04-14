from bson import ObjectId
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from mongoengine import DoesNotExist

from fitness_app.models import User, Workout, Routine, Follow, WorkoutLike, WorkoutComment, Notification, \
    AchievementGained, UserReport, WorkoutReport, Block
from fitness_app.utils.responses import error_response, success_response
from fitness_app.utils.serializer import serialize_documents, serialize_doc

users_bp = Blueprint('users', __name__)


@users_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
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
        "workouts": serialize_documents(Workout.objects(user=ObjectId(user_id))),
        "routines": serialize_documents(Routine.objects(user=ObjectId(user_id))),
        "followers": serialize_documents(Follow.objects(followed=ObjectId(user_id))),
        "following": serialize_documents(Follow.objects(follower=ObjectId(user_id))),
    }
    return success_response(user_data, 200)


@users_bp.route('/user/<user_id>', methods=['GET'])
@jwt_required()
def get_user_profile_by_id(user_id):

    user = User.objects(id=user_id).first()
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
        "workouts": serialize_documents(Workout.objects(user=ObjectId(user_id))),
        "routines": serialize_documents(Routine.objects(user=ObjectId(user_id))),
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

    # Get IDs of users who are blocked or have blocked the current user
    blocked_users_ids = [str(block.blocked.id) for block in Block.objects(blocking=user_id)] + \
                        [str(block.blocking.id) for block in Block.objects(blocked=user_id)]

    query = {}
    if username_query:
        query['username'] = {'$regex': username_query, '$options': 'i'}

    try:
        users_query = User.objects(__raw__=query, id__ne=ObjectId(user_id), id__nin=blocked_users_ids).skip(skip).limit(limit)
        users = list(users_query)
        # Serialize users to include username and profilePhotoUrl
        user_data = [{
            "_id": str(user.id),
            "username": user.username,
            "profilePhotoUrl": user.profilePhotoUrl
        } for user in users]
        total_users = User.objects(__raw__=query, id__ne=ObjectId(user_id), id__nin=blocked_users_ids).count()
        has_more = skip + limit < total_users

        return jsonify({
            'users': user_data,
            'hasMore': has_more
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@users_bp.route('/delete_account', methods=['DELETE'])
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

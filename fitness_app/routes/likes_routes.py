from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, DoesNotExist
from fitness_app.models import WorkoutLike, User, Workout, Notification

likes_bp = Blueprint('likes', __name__)


@likes_bp.route('/like/<workout_id>', methods=['POST'])
@jwt_required()
def like_workout(workout_id):
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
        workout = Workout.objects.get(id=workout_id)

        if WorkoutLike.objects(user_id=user, workout_id=workout).first():
            return jsonify({"message": "Workout already liked."}), 400

        new_like = WorkoutLike(user_id=user, workout_id=workout)
        new_like.save()

        # Check if the workout being liked is not the user's own workout
        if str(workout.user.id) != str(user_id):
            # Create a notification for the workout owner
            Notification(
                user=workout.user,  # Note that the notification's user is the workout owner, not the liker
                action='like',
                target_workout=workout,
                timestamp=datetime.utcnow()
            ).save()

        return jsonify({"message": "Workout liked successfully."}), 200
    except (ValidationError, DoesNotExist):
        return jsonify({"error": "Invalid user or workout ID."}), 400


@likes_bp.route('/unlike/<workout_id>', methods=['POST'])
@jwt_required()
def unlike_workout(workout_id):
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
        workout = Workout.objects.get(id=workout_id)

        like = WorkoutLike.objects(user_id=user, workout_id=workout).first()
        if not like:
            return jsonify({"message": "Workout not previously liked."}), 400

        # Delete the like
        like.delete()

        # Find and delete the corresponding notification
        notification = Notification.objects(user=user, action='like', target_workout=workout).first()
        if notification:
            notification.delete()

        return jsonify({"message": "Workout unlike successful."}), 200
    except (ValidationError, DoesNotExist):
        return jsonify({"error": "Invalid user or workout ID."}), 400


@likes_bp.route('/<workout_id>', methods=['GET'])
@jwt_required()
def fetch_workout_likes(workout_id):
    try:
        workout_likes = WorkoutLike.objects(workout_id=ObjectId(workout_id))
        likes_data = [{
                "user_id": str(like.user_id.id),
                "username": like.user_id.username,
                "profilePhotoUrl": like.user_id.profilePhotoUrl,
                "timestamp": like.timestamp
            }for like in workout_likes]

        return jsonify(likes_data), 200
    except ValidationError:
        return jsonify({"error": "Invalid workout ID."}), 400
    except DoesNotExist:
        return jsonify({"error": "Workout not found."}), 404

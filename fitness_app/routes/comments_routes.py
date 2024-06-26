from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError
from fitness_app.models import WorkoutComment, User, Notification, Workout
from fitness_app.utils.serializer import serialize_doc

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/comment/<workout_id>', methods=['POST'])
@jwt_required()
def add_comment(workout_id):
    user_id = get_jwt_identity()
    body = request.json.get('body')

    if not body:
        return jsonify({"error": "Comment body is required."}), 400

    try:
        initiator = User.objects.get(id=user_id)
        workout = Workout.objects.get(id=workout_id)

        new_comment = WorkoutComment(user=initiator, workout=workout, body=body)
        new_comment.save()

        if str(workout.user.id) != user_id:
            Notification(
                user=workout.user,
                initiator=initiator,
                action='comment',
                targetWorkout=workout,
            ).save()

        comment_data = serialize_doc(new_comment.to_mongo().to_dict())
        comment_data['user'] = {
            "_id": str(initiator.id),
            "username": initiator.username,
            "profilePhotoUrl": initiator.profilePhotoUrl
        }

        return jsonify(comment_data), 200
    except ValidationError:
        return jsonify({"error": "Invalid workout ID."}), 400


@comments_bp.route('/<workout_id>', methods=['GET'])
@jwt_required()
def fetch_comments(workout_id):
    try:
        comments = WorkoutComment.objects(workout=workout_id)

        comments_data = []

        for comment in comments:
            # Serialize the comment document
            comment_data = serialize_doc(comment.to_mongo().to_dict())

            # Fetch the user for each comment
            user = comment.user

            # Embed user details directly into the comment data
            comment_data['user'] = {
                "_id": str(user.id),
                "username": user.username,
                "profilePhotoUrl": user.profilePhotoUrl
            }

            comments_data.append(comment_data)

        comments_data.reverse()
        return jsonify(comments_data), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


@comments_bp.route('/delete/<comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        comment = WorkoutComment.objects.get(id=comment_id)

        # Delete the associated notification, using both the workout and the commenter
        Notification.objects(
            action='comment',
            targetWorkout=comment.workout,
            initiator=comment.user
        ).delete()

        comment.delete()
        return jsonify({"message": "Comment deleted successfully."}), 200
    except WorkoutComment.DoesNotExist:
        return jsonify({"error": "Comment not found."}), 404
    except ValidationError:
        return jsonify({"error": "Invalid comment ID."}), 400

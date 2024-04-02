from datetime import datetime

from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError
from fitness_app.models import WorkoutComment, User, Notification, Workout

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

        # Create a notification for the workout owner if the commenter isn't the owner
        if str(workout.user.id) != user_id:
            Notification(
                user=workout.user,  # Workout owner receives the notification
                initiator=initiator,  # The commenter
                action='comment',
                targetWorkout=workout,
                timestamp=datetime.utcnow()
            ).save()

        # Prepare and return the comment data
        comment_data = {
            "_id": str(new_comment.id),
            "workout_id": str(workout.id),
            "body": new_comment.body,
            "timestamp": new_comment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "user": {
                "_id": str(initiator.id),
                "username": initiator.username,
                "profilePhotoUrl": initiator.profilePhotoUrl
            }
        }

        return jsonify(comment_data), 200
    except ValidationError:
        return jsonify({"error": "Invalid workout ID."}), 400


@comments_bp.route('/<workout_id>', methods=['GET'])
@jwt_required()
def fetch_comments(workout_id):
    try:
        comments = WorkoutComment.objects(workout=workout_id)

        # This will hold the comments data including user details
        comments_data = []

        for comment in comments:

            # Fetch the user for each comment
            user = User.objects.get(id=comment.user.id)
            # Now, add the comment and user details to comments_data
            comments_data.append({
                "_id": str(comment.id),
                "workout_id": str(comment.workout.id),
                "body": comment.body,
                "timestamp": comment.timestamp,
                "user": {
                    "_id": str(comment.user.id),
                    "username": user.username,
                    "profilePhotoUrl": user.profilePhotoUrl
                }
            })

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
            initiator=comment.user  # Ensure to match the notification by the initiator
        ).delete()

        comment.delete()
        return jsonify({"message": "Comment deleted successfully."}), 200
    except WorkoutComment.DoesNotExist:
        return jsonify({"error": "Comment not found."}), 404
    except ValidationError:
        return jsonify({"error": "Invalid comment ID."}), 400

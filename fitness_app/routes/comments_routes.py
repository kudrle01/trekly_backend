from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError
from fitness_app.models import WorkoutComment, User

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/comment/<workout_id>', methods=['POST'])
@jwt_required()
def add_comment(workout_id):
    user_id = get_jwt_identity()
    body = request.json.get('body')

    if not body:
        return jsonify({"error": "Comment body is required."}), 400

    try:
        new_comment = WorkoutComment(user_id=user_id, workout_id=workout_id, body=body)
        new_comment.save()

        user = User.objects.get(id=user_id)

        # Serialize the new comment for the response
        comment_data = {
            "id": str(new_comment.id),
            "workout_id": str(new_comment.workout_id.id),
            "body": new_comment.body,
            "timestamp": new_comment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "user": {
                "_id": str(new_comment.user_id.id),
                "username": user.username,
                "profilePhotoUrl": user.profilePhotoUrl
            }
        }

        return jsonify(comment_data), 200
    except ValidationError:
        return jsonify({"error": "Invalid workout ID."}), 400


@comments_bp.route('/<workout_id>', methods=['GET'])
@jwt_required()
def fetch_comments(workout_id):
    try:
        comments = WorkoutComment.objects(workout_id=workout_id)

        # This will hold the comments data including user details
        comments_data = []

        for comment in comments:

            # Fetch the user for each comment
            user = User.objects.get(id=comment.user_id.id)
            # Now, add the comment and user details to comments_data
            comments_data.append({
                "_id": str(comment.id),
                "workout_id": str(comment.workout_id.id),
                "body": comment.body,
                "timestamp": comment.timestamp,
                "user": {
                    "_id": str(comment.user_id.id),
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
        # Find the comment by ID
        comment = WorkoutComment.objects.get(id=comment_id)
        comment.delete()
        return jsonify({"message": "Comment deleted successfully."}), 200
    except WorkoutComment.DoesNotExist:
        return jsonify({"error": "Comment not found."}), 404
    except ValidationError:
        return jsonify({"error": "Invalid comment ID."}), 400

from datetime import datetime

from bson import ObjectId
from flask import Blueprint, request, jsonify, json
from flask_jwt_extended import jwt_required, get_jwt_identity

from fitness_app.models import Workout, User, WorkoutLike, WorkoutComment, Follow
from mongoengine.errors import ValidationError

from fitness_app.utils.serializer import serialize_doc
from fitness_app.utils.upload_workout_image import upload_workout_image
from fitness_app.utils.validate_and_get_file import validate_and_get_file

workouts_bp = Blueprint('workouts', __name__)


@workouts_bp.route("/all", methods=["GET"])
@jwt_required()
def fetch_workouts():
    user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    skip = (page - 1) * limit
    feed_type = request.args.get('feedType', 'global')  # Default to 'global' if not specified

    try:
        if feed_type == 'followed':
            # Get the list of user_ids that the current user is following
            followed_users_ids = [str(follow.followed.id) for follow in Follow.objects(follower=user_id)]
            workouts_query = Workout.objects(user_id__in=followed_users_ids).order_by('-timestamp').skip(skip).limit(limit)
        else:
            # Exclude workouts from followed users in the global feed
            followed_users_ids = [str(follow.followed.id) for follow in Follow.objects(follower=user_id)]
            workouts_query = Workout.objects(user_id__nin=followed_users_ids, user_id__ne=user_id).order_by('-timestamp').skip(skip).limit(limit)

        # Enhance the workout data with likes and comments
        enhanced_workouts = []
        for workout in workouts_query:
            workout_data = serialize_doc(workout.to_mongo().to_dict())
            likes_count = WorkoutLike.objects(workout_id=workout.id).count()
            comments_count = WorkoutComment.objects(workout_id=workout.id).count()
            workout_data['likesCount'] = likes_count
            workout_data['commentsCount'] = comments_count
            enhanced_workouts.append(workout_data)

        total_workouts_count = workouts_query.count()
        has_more = skip + limit < total_workouts_count

        return jsonify({
            'workouts': enhanced_workouts,
            'hasMore': has_more
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@workouts_bp.route("/save", methods=["POST"])
@jwt_required()
def save_workout():
    user_id = get_jwt_identity()
    try:
        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
    except ValidationError:
        return jsonify({"error": "Invalid user_id"}), 400

    name = request.form.get('name')
    difficulty = request.form.get('difficulty')
    duration = int(request.form.get('duration', 0))
    postContent = request.form.get('postContent')
    exercises = json.loads(request.form.get('exercises', '[]'))

    current_date = datetime.now().date()
    if duration >= 600:
        # Check if the workout is the first one today
        if not user.lastStreakEvidence or user.lastStreakEvidence < current_date:
            # Update streak and last workout date
            user.streak += 1
            user.lastStreakEvidence = current_date
            user.save()

    imageUrl = None
    file, error = validate_and_get_file(request)
    if file:
        try:
            imageUrl = upload_workout_image(file)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Assuming you have a Workout model and save logic here
    workout = Workout(
        user_id=user,
        name=name,
        difficulty=difficulty,
        duration=duration,
        postContent=postContent,
        exercises=exercises,
        imageUrl=imageUrl  # This could be None if no file was uploaded
    )
    workout.save()

    return jsonify({"message": "Workout saved successfully", "workout_id": str(workout.id)}), 200


@workouts_bp.route('/delete/<workout_id>', methods=['DELETE'])
@jwt_required()
def delete_workout(workout_id):
    user_id = get_jwt_identity()
    try:
        workout = Workout.objects.get(id=workout_id, user_id=user_id)
        workout.delete()
        return jsonify({"message": "Workout deleted successfully"}), 200
    except Workout.DoesNotExist:
        return jsonify({"error": "Workout not found or not authorized to delete"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
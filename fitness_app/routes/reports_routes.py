from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine.errors import ValidationError, DoesNotExist

from fitness_app.models import User, Workout, UserReport, WorkoutReport, Block, Follow, WorkoutLike, WorkoutComment, Notification

reports_bp = Blueprint('reports', __name__)


# Report a user
@reports_bp.route('/report_user/<user_id>', methods=['POST'])
@jwt_required()
def report_user(user_id):
    reporter_id = get_jwt_identity()
    try:
        reporter = User.objects.get(id=reporter_id)
        reported = User.objects.get(id=user_id)

        if UserReport.objects(reporter=reporter, reported=reported).first():
            return jsonify({"message": "User already reported."}), 400

        report_data = request.json
        reason = report_data.get('reason', 'No reason provided')

        new_report = UserReport(
            reporter=reporter,
            reported=reported,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        new_report.save()

        return jsonify({"message": "User reported successfully."}), 200
    except (ValidationError, DoesNotExist):
        return jsonify({"error": "Invalid user ID."}), 400


# Report a workout
@reports_bp.route('/report_workout/<workout_id>', methods=['POST'])
@jwt_required()
def report_workout(workout_id):
    reporter_id = get_jwt_identity()
    try:
        reporter = User.objects.get(id=reporter_id)
        workout = Workout.objects.get(id=workout_id)

        if WorkoutReport.objects(reporter=reporter, workout=workout).first():
            return jsonify({"message": "Workout already reported."}), 400

        report_data = request.json
        reason = report_data.get('reason', 'No reason provided')

        new_report = WorkoutReport(
            reporter=reporter,
            workout=workout,
            reason=reason,
            timestamp=datetime.utcnow()
        )
        new_report.save()

        return jsonify({"message": "Workout reported successfully."}), 200
    except (ValidationError, DoesNotExist):
        return jsonify({"error": "Invalid workout ID."}), 400


@reports_bp.route('/block_user/<blocked_user_id>', methods=['POST'])
@jwt_required()
def block_user(blocked_user_id):
    blocking_user_id = get_jwt_identity()
    try:
        blocking_user = User.objects.get(id=blocking_user_id)
        blocked_user = User.objects.get(id=blocked_user_id)

        # Check if already blocked
        if Block.objects(blocking=blocking_user, blocked=blocked_user).first():
            return jsonify({"message": "User already blocked."}), 400

        # Create a new block entry
        block_entry = Block(blocking=blocking_user, blocked=blocked_user)
        block_entry.save()

        # Remove follows, likes, and comments from blocker to blocked
        Follow.objects(followed=blocked_user, follower=blocking_user).delete()
        Follow.objects(followed=blocking_user, follower=blocked_user).delete()
        WorkoutLike.objects(user=blocking_user, workout__in=Workout.objects(user=blocked_user)).delete()
        WorkoutLike.objects(user=blocked_user, workout__in=Workout.objects(user=blocking_user)).delete()
        WorkoutComment.objects(user=blocking_user, workout__in=Workout.objects(user=blocked_user)).delete()
        WorkoutComment.objects(user=blocked_user, workout__in=Workout.objects(user=blocking_user)).delete()
        Notification.objects(user=blocking_user, initiator=blocked_user).delete()
        Notification.objects(user=blocked_user, initiator=blocking_user).delete()


        return jsonify({"message": "User blocked successfully."}), 200
    except ValidationError:
        return jsonify({"error": "Invalid user ID."}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
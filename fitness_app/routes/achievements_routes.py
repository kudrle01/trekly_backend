from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist
from bson import ObjectId

from fitness_app.models import User, Achievement, AchievementGained, Workout

achievements_bp = Blueprint('achievements', __name__)


@achievements_bp.route('/check', methods=['GET'])
@jwt_required()
def check_achievements():
    current_user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=ObjectId(current_user_id))

        # Calculate workouts and workoutMinutes for the user
        workouts = Workout.objects(user=user).count()
        workoutMinutes = sum(workout.duration for workout in Workout.objects(user=user))/60

        all_achievements = Achievement.objects  # Fetch all achievements
        achievements_gained = AchievementGained.objects(user=user).only('achievement')
        gained_achievement_ids = {gained.achievement.id for gained in achievements_gained}

        newly_gained_achievements = []

        for achievement in all_achievements:
            if achievement.id in gained_achievement_ids:
                continue  # Skip if already gained

            conditions_met = all([
                (user.streak >= condition.streakNumber or condition.streakNumber == 0) and
                (workouts >= condition.workoutsNumber or condition.workoutsNumber == 0) and
                (workoutMinutes >= condition.minutes or condition.minutes == 0)
                for condition in achievement.conditions
            ])

            if conditions_met:
                AchievementGained(user=user, achievement=achievement).save()
                newly_gained_achievements.append({
                    "name": achievement.name,
                    "description": achievement.description
                })

        # Check if any achievements were gained
        if newly_gained_achievements:
            return jsonify(newly_gained_achievements), 200
        else:
            return jsonify([]), 200  # Return an empty list if no new achievements were gained

    except DoesNotExist:
        return jsonify({"message": "User not found"}), 404


@achievements_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def user_achievements(user_id):
    try:
        achievements_gained = AchievementGained.objects(user=ObjectId(user_id))

        achievements = [{
            "name": gain.achievement.name,
            "description": gain.achievement.description,
            "timestamp": gain.timestamp
        } for gain in achievements_gained]

        return jsonify(achievements), 200

    except DoesNotExist:
        return jsonify({"message": "User not found"}), 404


@achievements_bp.route('/all', methods=['GET'])
def list_achievements():
    achievements = Achievement.objects
    achievements_list = [{
        "name": achievement.name,
        "description": achievement.description,
        "conditions": achievement.conditions  # You might want to format this more nicely
    } for achievement in achievements]

    return jsonify(achievements_list), 200

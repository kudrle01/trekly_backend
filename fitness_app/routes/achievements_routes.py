from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import DoesNotExist

from fitness_app.models import User, AchievementGained, Achievement

achievements_bp = Blueprint('achievements', __name__)


@achievements_bp.route('/all', methods=['GET'])
def list_achievements():
    achievements = Achievement.objects.all()
    achievements_data = []
    for achievement in achievements:
        achievements_data.append({
            'id': str(achievement.id),
            'name': achievement.name,
            'description': achievement.description,
            'conditions': achievement.conditions
        })
    return jsonify(achievements_data), 200


@achievements_bp.route('/award/<achievement_id>', methods=['POST'])
@jwt_required()
def award_achievement(achievement_id):
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
        achievement = Achievement.objects.get(id=achievement_id)

        # Check if the user already has this achievement
        if AchievementGained.objects(user=user, achievement=achievement).first():
            return jsonify({'message': 'User already has this achievement'}), 400

        AchievementGained(user=user, achievement=achievement).save()
        return jsonify({'message': 'Achievement awarded successfully'}), 200
    except DoesNotExist:
        return jsonify({'error': 'User or achievement not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@achievements_bp.route('/user', methods=['GET'])
@jwt_required()
def user_achievements():
    user_id = get_jwt_identity()
    try:
        user = User.objects.get(id=user_id)
        achievements_gained = AchievementGained.objects(user=user)
        achievements_data = []
        for achievement in achievements_gained:
            achievements_data.append({
                'id': str(achievement.achievement.id),
                'name': achievement.achievement.name,
                'description': achievement.achievement.description,
                'awarded_on': achievement.timestamp
            })
        return jsonify(achievements_data), 200
    except DoesNotExist:
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



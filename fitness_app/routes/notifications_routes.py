from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from mongoengine import ValidationError

from fitness_app.models import Notification

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user_id = get_jwt_identity()

    try:
        # Fetch notifications where the current user is the target of the action
        notifications = Notification.objects(user=current_user_id).order_by('-timestamp')

        notifications_data = [{
            "action": notification.action,
            "timestamp": notification.timestamp,
            "user": str(notification.user.id),
            "username": notification.user.username,
            # Include other relevant data based on action type
        } for notification in notifications]

        return jsonify(notifications_data), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

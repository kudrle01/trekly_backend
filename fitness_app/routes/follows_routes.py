from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from fitness_app.models import Follow, User  # Adjust the import path as necessary
from mongoengine.errors import NotUniqueError

follows_bp = Blueprint('follows', __name__)


@follows_bp.route('/follow/<user_id>', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    current_user_id = get_jwt_identity()

    # Prevent users from following themselves
    if str(current_user_id) == user_id:
        return jsonify({"message": "You cannot follow yourself."}), 400

    # Ensure both users exist
    follower = User.objects(id=current_user_id).first()
    followed = User.objects(id=user_id).first()
    if not follower or not followed:
        return jsonify({"message": "User not found."}), 404

    # Check if already following
    if Follow.objects(followed=followed, follower=follower).first():
        return jsonify({"message": "Already following this user."}), 400

    # Create new follow relationship
    try:
        Follow(followed=followed, follower=follower).save()
    except NotUniqueError:
        return jsonify({"error": "Follow relationship already exists."}), 400

    return jsonify({"message": "Successfully followed the user."}), 200


@follows_bp.route('/unfollow/<user_id>', methods=['POST'])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = get_jwt_identity()

    follower = User.objects(id=current_user_id).first()
    followed = User.objects(id=user_id).first()

    # Check if relationship exists
    follow_relationship = Follow.objects(followed=followed, follower=follower).first()
    if not follow_relationship:
        return jsonify({"message": "Not following this user."}), 400

    # Remove follow relationship
    follow_relationship.delete()
    return jsonify({"message": "Successfully unfollowed the user."}), 200


@follows_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def fetch_follows_by_user_id(user_id):

    # Fetching followers: those who follow the current user
    followers_relations = Follow.objects(followed=user_id)
    followers = User.objects(id__in=[relation.follower.id for relation in followers_relations])
    followers_data = [{'_id': str(user.id), 'username': user.username, 'profilePhotoUrl': user.profilePhotoUrl} for user in followers]

    # Fetching following: those the current user is following
    following_relations = Follow.objects(follower=user_id)
    following = User.objects(id__in=[relation.followed.id for relation in following_relations])
    following_data = [{'_id': str(user.id), 'username': user.username, 'profilePhotoUrl': user.profilePhotoUrl} for user in following]

    return jsonify({
        'followers': followers_data,
        'following': following_data
    }), 200



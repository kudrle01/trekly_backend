import os

from bson import ObjectId
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity

from fitness_app.models import Exercise, User
from fitness_app.utils.upload_user_profile_image import upload_user_profile_image
from fitness_app.utils.validate_and_get_file import validate_and_get_file

images_bp = Blueprint('images', __name__)


@images_bp.route('/upload/user', methods=['POST'])
@jwt_required()
def upload_image():
    user_id = get_jwt_identity()
    user = User.objects(id=ObjectId(user_id)).first()
    file, error_message = validate_and_get_file(request)
    if error_message:
        return jsonify({'error': error_message}), 400

    try:
        user.profilePhotoUrl = upload_user_profile_image(file, user_id)
        user.save()
        return jsonify({'url': user.profilePhotoUrl}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@images_bp.route('/exercises/<exercise_id>', methods=['GET'])
def exercise_image(exercise_id):
    exercise = Exercise.objects.with_id(exercise_id)
    exercise_name = exercise.name
    # Generate the URL for the image
    sanitized_id = exercise_name.lower().replace("-", "").replace("(", "").replace(")", "").replace("°", "").replace(
        "/", "")
    image_url, options = cloudinary_url(f"exercises/{sanitized_id}", secure=True)
    https_url = image_url.replace('http://', 'https://')
    return https_url


@images_bp.route('/exercises-static/<exercise_id>', methods=['GET'])
def exercise_static_image(exercise_id):
    exercise = Exercise.objects.with_id(exercise_id)
    exercise_name = exercise.name
    # Generate the URL for the image
    sanitized_id = exercise_name.lower().replace("-", "").replace("(", "").replace(")", "").replace("°", "").replace(
        "/", "")
    image_url, options = cloudinary_url(f"exercises_static/{sanitized_id}", secure=True)
    https_url = image_url.replace('http://', 'https://')
    return https_url


@images_bp.route('/user/<user_id>', methods=['GET'])
def user_image(user_id):
    image_url, options = cloudinary_url(f"userProfile/{user_id}", secure=True)
    return redirect(image_url)


@images_bp.route('/posts/<post_id>', methods=['GET'])
def post_image(post_id):
    image_url, options = cloudinary_url(f"posts/{post_id}", secure=True)
    https_url = image_url.replace('http://', 'https://')
    return redirect(https_url)

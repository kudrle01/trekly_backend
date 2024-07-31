from cloudinary.uploader import upload


def upload_user_profile_image(file, user_id):
    """
    Uploads a user profile image to Cloudinary.

    Args:
        file: The file object to upload.
        user_id: The user's unique identifier.

    Returns:
        The URL of the uploaded image on success.

    Raises:
        Exception: If the file fails to upload or if an error occurs.
    """
    try:
        folder = 'user/'
        public_id = f'{folder}{user_id}'
        result = upload(file, allowed_formats=['jpg', 'png', 'gif'], public_id=public_id, secure=True)
        return result
    except Exception as e:
        raise Exception(f'Failed to upload image. {str(e)}')

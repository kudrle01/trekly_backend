from cloudinary.uploader import upload


def upload_workout_image(file):
    """
    Uploads a workout image to Cloudinary without specifying a public_id.

    Args:
        file: The file object to upload.

    Returns:
        A tuple of the URL of the uploaded image and its generated public_id on success.

    Raises:
        Exception: If the file fails to upload or if an error occurs.
    """
    try:
        folder = 'posts/'
        result = upload(file, allowed_formats=['jpg', 'png', 'gif'], folder=folder, secure=True)
        return result
    except Exception as e:
        raise Exception(f'Failed to upload image. {str(e)}')

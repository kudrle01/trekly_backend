import os


def validate_and_get_file(request, max_file_size=10485760):
    """
    Validates the uploaded file's presence, selection, and size.

    Args:
        request: The Flask request object.
        max_file_size: Maximum allowed file size in bytes.

    Returns:
        A tuple containing (file, error_message). If the file is valid, error_message will be None.

    """
    if 'file' not in request.files:
        return None, 'No file part'

    file = request.files['file']
    if file.filename == '':
        return None, 'No selected file'

    # Check the size of the file without reading its content
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)  # Reset file pointer
    if file_length > max_file_size:
        return None, 'File size too large. Maximum allowed size is 10MB.'

    return file, None

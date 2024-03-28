import bcrypt


def hash_password(plain_text_password):
    # Convert the plain text password to bytes
    password_bytes = plain_text_password.encode('utf-8')

    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password


def check_password(plain_text_password, hashed_password):
    # Convert the plain text password to bytes
    password_bytes = plain_text_password.encode('utf-8')

    # Convert the hashed password to bytes (if it's not already)
    hashed_password_bytes = hashed_password if isinstance(hashed_password, bytes) else hashed_password.encode('utf-8')

    # Check if the provided password matches the stored hashed password
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# app.py or wherever you define your Flask application
from datetime import timedelta
from flask import Flask
from flask_cors import CORS, cross_origin
import os
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
from flask_jwt_extended import JWTManager
from flask_mongoengine import MongoEngine

# routes/blueprints
from .routes.auth_routes import auth_bp
from .routes.comments_routes import comments_bp
from .routes.exercises_routes import exercises_bp
from .routes.follows_routes import follows_bp
from .routes.images_routes import images_bp
from .routes.likes_routes import likes_bp
from .routes.notifications_routes import notifications_bp
from .routes.routines_routes import routines_bp
from .routes.workouts_routes import workouts_bp
from .routes.users_routes import users_bp
from .routes.achievements_routes import achievements_bp


from .utils.reset_user_streaks import reset_user_streaks
from .utils.refill_rest_days import refill_rest_days
import cloudinary

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

jwt = JWTManager()
db = MongoEngine()


def create_app():
    app = Flask(__name__, static_folder='fitness_app/build')
    CORS(app)

    # Configuration settings
    MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USER')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}/?retryWrites=true&w=majority"
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['MONGODB_SETTINGS'] = {
        'host': MONGO_URI,
        'db': os.getenv('DATABASE_NAME'),
    }
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['HOST'] = os.getenv('HOST')
    app.config['PORT'] = int(os.getenv('PORT'))
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    app.config['CLOUDINARY_CLOUD_NAME'] = os.getenv('CLOUDINARY_CLOUD_NAME')
    app.config['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
    app.config['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')
    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET']
    )

    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Initialize extensions
    jwt.init_app(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(exercises_bp, url_prefix='/exercises')
    app.register_blueprint(images_bp, url_prefix='/images')
    app.register_blueprint(routines_bp, url_prefix='/routines')
    app.register_blueprint(workouts_bp, url_prefix='/workouts')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(follows_bp, url_prefix='/follows')
    app.register_blueprint(likes_bp, url_prefix='/likes')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    app.register_blueprint(achievements_bp, url_prefix='/achievements')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(id='Reset Streaks', func=reset_user_streaks, trigger='cron', hour=0, minute=1)
    scheduler.add_job(id='Refill Rest Days', func=refill_rest_days, trigger='cron', day=1, hour=0, minute=1)

    return app

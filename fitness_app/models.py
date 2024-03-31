from mongoengine import Document, StringField, EmailField, IntField, DateTimeField, DateField, EmbeddedDocument, \
    EmbeddedDocumentField, ListField, URLField, ReferenceField, BooleanField
import datetime


# User model
class User(Document):
    username = StringField(max_length=100, required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)
    birthDate = DateField(required=True)
    gender = StringField(required=True)
    registrationDate = DateTimeField(default=datetime.datetime.now)
    profilePhotoUrl = StringField(default=None)
    lastStreakEvidence = DateField()
    streak = IntField(default=0)
    restDays = IntField(default=10)

    meta = {'collection': 'users'}


class AchievementCondition(EmbeddedDocument):
    streakNumber = IntField(default=0)
    workoutsNumber = IntField(default=0)
    minutes = IntField(default=0)


class Achievement(Document):
    name = StringField(max_length=100, required=True)
    description = StringField(required=True)
    conditions = ListField(EmbeddedDocumentField(AchievementCondition), required=True)

    meta = {'collection': 'achievements'}


class AchievementGained(Document):
    user = ReferenceField(User, required=True)
    achievement = ReferenceField(Achievement, required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'achievementsGained'}


class Follow(Document):
    followed = ReferenceField(User, required=True, dbref_id_field='id_followed')
    follower = ReferenceField(User, required=True, dbref_id_field='id_following')
    timestamp = DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'follows'}


class BodyPart(Document):
    name = StringField(required=True)
    pplPlan = StringField(required=True)
    ulPlan = StringField(required=True)

    meta = {'collection': 'bodyParts'}


class Equipment(Document):
    name = StringField(required=True)
    type = StringField(required=True)

    meta = {'collection': 'equipment'}


class ExerciseSet(EmbeddedDocument):
    kilograms = StringField(required=False, default='')
    reps = StringField(required=False, default='')
    isDone = BooleanField(required=True, default=False)


class Exercise(Document):
    bodyPart = ReferenceField(BodyPart, required=True)
    equipment = ReferenceField(Equipment, required=True)
    name = StringField(required=True)  # Consider adding if exercises have names or identifiers
    target = StringField(required=True)
    secondaryMuscles = ListField(StringField())
    instructions = ListField(StringField())

    meta = {'collection': 'exercises'}


class WorkoutExercise(EmbeddedDocument):
    _id = ReferenceField(Exercise, required=True)
    sets = ListField(EmbeddedDocumentField(ExerciseSet))


class Routine(Document):
    user_id = ReferenceField(User, required=True)
    name = StringField(max_length=100, required=True)
    exercises = ListField(EmbeddedDocumentField(WorkoutExercise), required=True)

    meta = {'collection': 'routines'}


class Workout(Document):
    user_id = ReferenceField(User, required=True)
    name = StringField(max_length=100, required=True)
    duration = IntField(required=True)
    difficulty = IntField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    imageUrl = StringField(default=None)
    postContent = StringField(max_length=100)
    exercises = ListField(EmbeddedDocumentField(WorkoutExercise), required=True)

    meta = {'collection': 'workouts'}


class WorkoutLike(Document):
    user_id = ReferenceField(User, required=True)
    workout_id = ReferenceField(Workout, required=True)  # Assuming a Post model exists
    timestamp = DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'workoutLikes'}


class WorkoutComment(Document):
    user_id = ReferenceField(User, required=True)
    workout_id = ReferenceField(Workout, required=True)
    body = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'workoutComments'}


class Notification(Document):
    user_id = ReferenceField(User, required=True)
    action = StringField(required=True)
    target_workout = ReferenceField(Workout, required=False)
    timestamp = DateTimeField(required=True)
    meta = {'collection': 'notifications'}
from mongoengine import Document, StringField, EmailField, IntField, DateTimeField, DateField, EmbeddedDocument, \
    EmbeddedDocumentField, ListField, URLField, ReferenceField, BooleanField
from datetime import datetime, timezone


# User model with indexing on username and email for faster lookup.
class User(Document):
    username = StringField(max_length=100, required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)
    birthDate = DateField(required=True)
    gender = StringField(required=True)
    registrationDate = DateTimeField(default=lambda: datetime.now(timezone.utc))
    profilePhotoUrl = StringField(default=None)
    lastStreakEvidence = DateField()
    streak = IntField(default=0)
    restDays = IntField(default=10)

    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True, 'background': True},
            {'fields': ['email'], 'unique': True, 'background': True},
        ]
    }


class AchievementCondition(EmbeddedDocument):
    streakNumber = IntField(default=0)
    workoutsNumber = IntField(default=0)
    minutes = IntField(default=0)


# Indexing might not be directly applicable for Achievement as it heavily depends on use cases.
class Achievement(Document):
    name = StringField(max_length=100, required=True)
    description = StringField(required=True)
    conditions = ListField(EmbeddedDocumentField(AchievementCondition), required=True)

    meta = {
        'collection': 'achievements',
        'indexes': [
            {'fields': ['name'], 'background': True},
        ]
    }


class AchievementGained(Document):
    user = ReferenceField(User, required=True)
    achievement = ReferenceField(Achievement, required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'achievementsGained',
        'indexes': [
            {'fields': ['user', 'achievement'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }


class Follow(Document):
    followed = ReferenceField(User, required=True, dbref_id_field='id_followed')
    follower = ReferenceField(User, required=True, dbref_id_field='id_following')
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'follows',
        'indexes': [
            {'fields': ['followed', 'follower'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }


class BodyPart(Document):
    name = StringField(required=True)
    pplPlan = StringField(required=True)
    ulPlan = StringField(required=True)

    meta = {
        'collection': 'bodyParts',
        'indexes': [
            {'fields': ['name'], 'background': True},
        ]
    }


class Equipment(Document):
    name = StringField(required=True)
    type = StringField(required=True)

    meta = {
        'collection': 'equipment',
        'indexes': [
            {'fields': ['name'], 'background': True},
        ]
    }


class ExerciseSet(EmbeddedDocument):
    kilograms = StringField(required=False, default='')
    reps = StringField(required=False, default='')
    isDone = BooleanField(required=True, default=False)


class Exercise(Document):
    bodyPart = ReferenceField(BodyPart, required=True)
    equipment = ReferenceField(Equipment, required=True)
    name = StringField(required=True)
    target = StringField(required=True)
    secondaryMuscles = ListField(StringField())
    instructions = ListField(StringField())

    meta = {
        'collection': 'exercises',
        'indexes': [
            {'fields': ['bodyPart', 'equipment'], 'background': True},
        ]
    }


class WorkoutExercise(EmbeddedDocument):
    _id = ReferenceField(Exercise, required=True)
    sets = ListField(EmbeddedDocumentField(ExerciseSet))


class Routine(Document):
    user = ReferenceField(User, required=True)
    name = StringField(max_length=100, required=True)
    exercises = ListField(EmbeddedDocumentField(WorkoutExercise), required=True)

    meta = {
        'collection': 'routines',
        'indexes': [
            {'fields': ['user'], 'background': True},
        ]
    }


class Workout(Document):
    user = ReferenceField(User, required=True)
    name = StringField(max_length=100, required=True)
    duration = IntField(required=True)
    difficulty = IntField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    imageUrl = StringField(default=None)
    postContent = StringField(max_length=100)
    exercises = ListField(EmbeddedDocumentField(WorkoutExercise), required=True)

    meta = {
        'collection': 'workouts',
        'indexes': [
            {'fields': ['user'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }


class WorkoutLike(Document):
    user = ReferenceField(User, required=True)
    workout = ReferenceField(Workout, required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'workoutLikes',
        'indexes': [
            {'fields': ['user', 'workout'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }


class WorkoutComment(Document):
    user = ReferenceField(User, required=True)
    workout = ReferenceField(Workout, required=True)
    body = StringField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'workoutComments',
        'indexes': [
            {'fields': ['user', 'workout'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }


class Notification(Document):
    user = ReferenceField(User, required=True)
    initiator = ReferenceField(User, required=True)
    action = StringField(required=True)
    targetWorkout = ReferenceField(Workout, required=False)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {
        'collection': 'notifications',
        'indexes': [
            {'fields': ['user'], 'background': True},
            {'fields': ['timestamp'], 'background': True},
        ]
    }

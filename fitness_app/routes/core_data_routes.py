import os

from bson import ObjectId
from flask import jsonify, Blueprint, request
from fitness_app.models import BodyPart, Equipment, Exercise
from fitness_app.utils.serializer import serialize_doc
from fitness_app.utils.responses import success_response, error_response

core_data_bp = Blueprint('core-data', __name__)


@core_data_bp.route("/bodyParts", methods=["GET"])
def get_body_parts_list():
    body_parts = BodyPart.objects.all()
    serialized_body_parts = [serialize_doc(body_part.to_mongo().to_dict()) for body_part in body_parts]
    return jsonify(serialized_body_parts)


@core_data_bp.route("/bodyParts/<_id>", methods=["GET"])
def get_body_part(_id):
    body_part = BodyPart.objects.with_id(_id)
    if not body_part:
        return error_response("Body part not found", 404)
    return body_part.to_json()


@core_data_bp.route("/equipment", methods=["GET"])
def get_equipment_list():
    equipment = Equipment.objects.all()
    serialized_equipment = [serialize_doc(eq.to_mongo().to_dict()) for eq in equipment]
    return jsonify(serialized_equipment)


@core_data_bp.route("/equipment/<_id>", methods=["GET"])
def get_equipment(_id):
    eq = Equipment.objects.with_id(_id)
    if not eq:
        return error_response("Equipment not found", 404)
    return eq.to_json()


@core_data_bp.route("/exercise", methods=["GET"])
def get_exercises():
    page_str = request.args.get('page', '1')
    limit_str = request.args.get('limit', '20')

    page = int(page_str) if page_str.isdigit() else 1
    limit = int(limit_str) if limit_str.isdigit() else 20

    body_part = request.args.get('bodyPart', '')
    equipment = request.args.get('equipment', '')
    name_query = request.args.get('query', '')
    skip = (page - 1) * limit

    query = {}
    if body_part:
        query['bodyPart'] = ObjectId(body_part)
    if equipment:
        query['equipment'] = ObjectId(equipment)
    if name_query:
        query['name'] = {'$regex': name_query, '$options': 'i'}

    try:
        exercises_query = Exercise.objects(__raw__=query).skip(skip).limit(limit)
        exercises = list(exercises_query)
        serialized_exercises = [serialize_doc(exercise.to_mongo().to_dict()) for exercise in exercises]
        total_exercises = Exercise.objects(__raw__=query).count()
        has_more = skip + limit < total_exercises

        return jsonify({
            'exercises': serialized_exercises,
            'hasMore': has_more
        }), 200
    except Exception as e:
        return error_response(str(e), 500)


@core_data_bp.route("/exercises/<exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    exercise = Exercise.objects.with_id(exercise_id)
    serialized_exercise = serialize_doc(exercise.to_mongo().to_dict())
    if not exercise:
        return error_response("Equipment not found", 404)
    return jsonify(serialized_exercise)

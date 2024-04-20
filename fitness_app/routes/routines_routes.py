from bson import ObjectId
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from fitness_app.models import Routine, ExerciseSet, WorkoutExercise
from fitness_app.utils.serializer import serialize_doc, serialize_documents

routines_bp = Blueprint('routines', __name__)


@routines_bp.route("/all", methods=['POST'])
@jwt_required()
def fetch_routines():
    user_id = get_jwt_identity()
    routines = Routine.objects(user=ObjectId(user_id)).first()
    return jsonify([serialize_doc(routine.to_mongo().to_dict()) for routine in routines])


@routines_bp.route("/save", methods=['POST'])
@jwt_required()
def save_routine():
    user_id = get_jwt_identity()
    name = request.json.get('name')
    exercises_data = request.json.get('exercises', [])

    routine_exercises = []
    for ex_data in exercises_data:
        exercise_id = ex_data.get('_id')
        sets_data = ex_data.get('sets', [])

        routine_exercise = WorkoutExercise(
            _id=ObjectId(exercise_id),
            sets=[ExerciseSet(**set_data) for set_data in sets_data]
        )
        routine_exercises.append(routine_exercise)

    try:
        routine = Routine(
            user=ObjectId(user_id),
            name=name,
            exercises=routine_exercises
        ).save()
        return jsonify({"message": "Routine saved successfully", "routine_id": str(routine.id)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routines_bp.route("/delete/<routine_id>", methods=['DELETE'])
@jwt_required()
def delete_routine(routine_id):
    user_id = get_jwt_identity()

    if not routine_id:
        return jsonify({"error": "Routine ID is required"}), 400

    try:
        routine_id = ObjectId(routine_id)
    except:
        return jsonify({"error": "Invalid Routine ID format"}), 400

    result = Routine.objects(id=routine_id).delete()

    if result == 0:
        return jsonify({"error": "Routine not found"}), 404

    routines = {
        "routines": serialize_documents(Routine.objects(user=ObjectId(user_id))),
    }
    return jsonify(routines), 200


@routines_bp.route("/update/<routine_id>", methods=['PUT'])
@jwt_required()
def update_routine(routine_id):
    update_data = request.json
    result = Routine.objects(id=ObjectId(routine_id)).update_one(**update_data)  # Update the routine

    if result == 0:
        return jsonify({"error": "Routine not found"}), 404

    updated_routine = Routine.objects.get(id=routine_id)  # Fetch the updated routine
    return jsonify(updated_routine.to_json()), 200

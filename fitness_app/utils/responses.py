from flask import make_response, jsonify


def error_response(message, status_code):
    response = jsonify({"success": False, "msg": message})
    return make_response(response, status_code)


def success_response(data, status_code=200):
    data["success"] = True
    response = jsonify(data)
    return make_response(response, status_code)

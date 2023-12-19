from flask import request
from app import app

class MissingFieldException(Exception):
    code = 400
    message = "Missing field"

def validate_form_fields(fields):
    for field in fields:
        if field not in request.form:
            raise MissingFieldException(f'Missing field: {field}')
    return {field: request.form[field] for field in fields}

@app.errorhandler(MissingFieldException)
def handle_missing_field_exception(error):
    return str(error), error.code

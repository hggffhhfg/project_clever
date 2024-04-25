from pydantic import ValidationError

from api import api
from api.exceptions.errors import NotFoundError
from common.pydantic_schemas.errors.message import ErrorResponse


@api.errorhandler(ValidationError)
def handler_bad_request_400(error: ValidationError):
    status = 400
    response = ErrorResponse(
        errors_count=error.error_count(),
        message=error.errors()
    )
    response = response.model_dump()
    return response, status


@api.errorhandler(ValidationError)
def handler_unprocessable_entity_422(error: ValidationError):
    status = 422
    response = ErrorResponse(message=error.errors())
    response = response.model_dump()
    return response, status


@api.errorhandler(NotFoundError)
def handler_not_found_404(error: NotFoundError):
    status = 404
    response = ErrorResponse(message=error.message)
    response = response.model_dump()
    return response, status
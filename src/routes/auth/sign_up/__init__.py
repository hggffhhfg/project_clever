from src.pydantic_schemas.user import UserCredentials
from src.routes.auth import ns_auth
from src.utils.payload import create_payload_from_model
from src.utils.restx_schema import response_schema
from src.utils.status_codes import HTTP

response_created_201 = "User is created"
response_model_201 = response_schema(
    code=HTTP.CREATED_201,
    ns=ns_auth,
    description=response_created_201,
)
response_conflict_409 = "Username is already taken"
response_model_409 = response_schema(
    code=HTTP.CONFLICT_409,
    ns=ns_auth,
    description=response_conflict_409,
)
signup_params = create_payload_from_model("form", UserCredentials)

from src.routes.auth.sign_up.sign_up import SignUpUserRoute  # noqa

signup_endpoint = "signup"
ns_auth.add_resource(
    SignUpUserRoute,
    f"/{signup_endpoint}",
    endpoint=signup_endpoint,
)
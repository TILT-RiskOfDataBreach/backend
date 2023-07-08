from pydantic import BaseModel


class ModelMessage(BaseModel):
    message: str


class ModelAcknowledged(BaseModel):
    acknowledged: bool


default_responses = {
    200: {"model": ModelAcknowledged},
    403: {"model": ModelMessage, "description": "Insufficient authorization level."},
}

unauth_response = {
	403: {"model": ModelMessage, "description": "Insufficient authorization level."}
}

import pytest
from flask.testing import FlaskClient
from pydantic import ValidationError

from common.baseclasses.response import Response
from common.baseclasses.status_codes import HTTP
from common.generators.diary import SleepDiaryGenerator
from common.generators.note import SleepNoteGenerator
from common.pydantic_schemas.errors.message import ErrorResponse
from common.pydantic_schemas.sleep.notes import SleepNoteModel, SleepNote, SleepNoteCompute


@pytest.mark.sleep
@pytest.mark.sleep_post
class TestSleepNotesPost(HTTP):
    ROUTE = "/api/sleep"
    RESPONSE_MODEL_201 = SleepNoteModel
    RESPONSE_MODEL_422 = ErrorResponse

    @pytest.mark.sleep_201
    @pytest.mark.repeat(10)
    def test_create_new_sleep_note_201(self, app, db_user_id: int, client: FlaskClient):
        new_note = SleepDiaryGenerator(db_user_id)
        created_note: SleepNoteCompute = new_note.create_note()
        json_body: dict = created_note.model_dump(mode='json', by_alias=True, exclude={'user_id', 'id'})
        response = client.post(self.ROUTE, json=json_body, query_string={'user_id': db_user_id})
        response = Response(response)
        response.assert_status_code(self.CREATED_201)
        response.validate(self.RESPONSE_MODEL_201)
        response.assert_data(created_note)

    @pytest.mark.sleep_post_422
    @pytest.mark.repeat(10)
    def test_create_new_sleep_note_422(self, app, db_user_id, client: FlaskClient):
        random_note_wrong_values = SleepNoteGenerator().wrong_note(mode='json')
        response = client.post(self.ROUTE, json=random_note_wrong_values)
        response = Response(response)

        with pytest.raises(ValidationError) as exc_info:
            SleepNote(**random_note_wrong_values)
        errors = self.RESPONSE_MODEL_422(message=exc_info.value.errors())
        response.assert_status_code(self.UNPROCESSABLE_ENTITY_422)
        response.validate(self.RESPONSE_MODEL_422)
        response.assert_data(errors)

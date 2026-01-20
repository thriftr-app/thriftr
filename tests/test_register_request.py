import pytest
from backend.auth.models.register_request import RegisterRequest
from pydantic import ValidationError

def test_no_email():
    with pytest.raises(ValidationError):
        RegisterRequest(username="mycooluser", password="OMVkVmioEv389Smoiawd*@")

def test_no_username():
    with pytest.raises(ValidationError):
        RegisterRequest(email="superlegitemail@google.com", password="oKFPEOkPKV*#V#*(v3k*(#V*(")

def test_valid_request():
    request = RegisterRequest(email="ajlgarza@colostate.edu", username="ayden", password="$uP3rS$ecr37P4$$vv0RD")
    assert request.email == 'ajlgarza@colostate.edu' 

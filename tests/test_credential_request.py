import pytest
from pydantic import ValidationError
from backend.models.login_request import LoginRequest

def test_no_user_or_email():
    with pytest.raises(ValidationError):
        LoginRequest(password="oijVJ*($jVo38iA")

def test_no_at_sign_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="dkowkdokd", password="jV8v89$jvIOaj8")

@pytest.mark.parametrize("email", ["@gmail.com", "dd@gmail.com", "normal@google", "normal@normal.", "normal@n.c", "normal@cdcdc."])

def test_invalid_emails(email):
    with pytest.raises(ValidationError) as test_info:
        LoginRequest(email=email, password = "iV9%*FFf%jfi2f9")

    print(str(test_info.value))

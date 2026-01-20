import pytest
from backend.auth.models.register_request import RegisterRequest
from backend.auth.models.login_request import LoginRequest
from fastapi.testclient import TestClient
from backend.app import app
from tests.test_registration import cleanup_account
import os

client = TestClient(app)

def test_temporary_login():
    username = 'tempuser'
    email = 'temp@realemail.com'
    password= 'eXtR3m3ly$trongP@ssw0rd!'
    cleanup_account(username)

    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    register_response = client.post('api/auth/register', json=register_request)
    assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    response_data = login_response.json()
    assert login_response.status_code == 200, f"Login failed: {login_response.text}" 
    assert 'access_token' in response_data, "Access token not found in login response"
    assert response_data['token_type'] == 'bearer', "Token type is not 'bearer'"

    token = response_data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    current_user_response = client.get('api/auth/current_user', headers=headers)
    assert current_user_response.status_code == 200, f"Fetching current user failed: {current_user_response.text}"
    user_data = current_user_response.json()
    assert user_data['username'] == username, "Fetched username does not match"
    assert user_data['email'] == email, "Fetched email does not match"  
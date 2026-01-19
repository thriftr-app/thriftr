import pytest
from backend.auth.models.register_request import RegisterRequest
from fastapi.testclient import TestClient
from backend.app import app
import os

client = TestClient(app)

def cleanup_account(identifier: str):
    lookup_result = client.get('api/db/accounts/lookup', params={'identifier': identifier}).json()
    
    if lookup_result.get('found'):
        delete_result = client.delete('api/db/accounts/delete', params={'identifier': identifier})
        assert delete_result.status_code == 200, f"Failed to delete account {identifier} during cleanup."
    

def test_dupe_username():
    username = 'test'
    email_a='test@test.com'
    email_b='test1@test.com'
    password='ver1s3cretP@SS'

    cleanup_account(username)


    request_a = RegisterRequest(username=username, email=email_a, password=password).model_dump()
    request_b = RegisterRequest(username=username, email=email_b, password=password).model_dump()

    first_register = client.post('api/auth/register', json=request_a)
    assert first_register.status_code == 200

    second_register = client.post('api/auth/register', json=request_b)
    assert second_register.status_code == 409

def test_dupe_email():
    username_a = 'test'
    username_b = 'testb'
    email='test@test.com'
    password='ver1s3cretP@SS'

    cleanup_account(email)


    request_a = RegisterRequest(username=username_a, email=email, password=password).model_dump()
    request_b = RegisterRequest(username=username_b, email=email, password=password).model_dump()

    first_register = client.post('api/auth/register', json=request_a)
    assert first_register.status_code == 200

    second_register = client.post('api/auth/register', json=request_b)
    assert second_register.status_code == 409
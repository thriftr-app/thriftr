import pytest
from fastapi import HTTPException
from backend.models.register_request import RegisterRequest
from fastapi.testclient import TestClient
from backend.app import app
import os

client = TestClient(app)


def test_dupe_username():
    username = 'test'
    email='test@test.com'
    password='ver1s3cretP@SS'

    lookup_result = client.post('db/accounts/lookup', json={'identifier': username}).json()

    if lookup_result.get('found'):
        delete_result = client.post('db/accounts/delete', json={'identifier': username}).json()
        assert delete_result.status_code == 200

    request = RegisterRequest(username=username, email=email, password=password).model_dump()

    first_register = client.post('auth/register', json=request)
    assert first_register.status_code == 200

    second_register = client.post('auth/register', json=request)
    assert second_register.status_code == 409

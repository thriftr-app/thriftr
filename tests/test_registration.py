import pytest
from fastapi import HTTPException
from backend.models.register_request import RegisterRequest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_dupe_username():
    req = RegisterRequest(username="test", email="test@test.com", password='ver1s3cretP@SS')
    pass

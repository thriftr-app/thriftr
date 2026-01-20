import pytest
from backend.auth.models.register_request import RegisterRequest
from backend.auth.models.login_request import LoginRequest
from fastapi.testclient import TestClient
from backend.app import app
from tests.test_registration import cleanup_account
from jose import jwt
import os
import time

client = TestClient(app)

# ============ SUCCESSFUL LOGIN TESTS ============

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

def test_login_with_username():
    """Test login using username instead of email"""
    username = 'testuser123'
    email = 'testuser@example.com'
    password = 'SecurePass123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login with username
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    cleanup_account(username)

def test_login_with_email():
    """Test login using email instead of username"""
    username = 'testuser456'
    email = 'testemail@example.com'
    password = 'SecurePass456!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login with email
    login_request = LoginRequest(email=email, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    cleanup_account(username)

# ============ INVALID CREDENTIALS TESTS ============

def test_login_nonexistent_user():
    """Test login with username that doesn't exist"""
    login_request = LoginRequest(username='nonexistentuser999', password='Password123!').model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 401
    assert 'detail' in response.json()

def test_login_nonexistent_email():
    """Test login with email that doesn't exist"""
    login_request = LoginRequest(email='nonexistent@fake.com', password='Password123!').model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 401

def test_login_wrong_password():
    """Test login with correct username but wrong password"""
    username = 'wrongpasstest'
    email = 'wrongpass@test.com'
    password = 'CorrectPass123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login with wrong password
    login_request = LoginRequest(username=username, password='WrongPassword456!').model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 401
    assert 'detail' in response.json()
    cleanup_account(username)

def test_login_case_sensitive_password():
    """Test that passwords are case sensitive"""
    username = 'casetest'
    email = 'case@test.com'
    password = 'CaseSensitive123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Try with different case
    login_request = LoginRequest(username=username, password='casesenSitive123!').model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 401
    cleanup_account(username)

def test_login_empty_password():
    """Test login with empty password"""
    login_request = {"username": "someuser", "password": ""}
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 422  # Validation error

def test_login_missing_password():
    """Test login without password field"""
    login_request = {"username": "someuser"}
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 422  # Validation error

def test_login_missing_identifier():
    """Test login without username or email"""
    login_request = {"password": "Password123!"}
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 422  # Validation error

# ============ TOKEN VALIDATION TESTS ============

def test_jwt_token_structure():
    """Test that the JWT token has valid structure"""
    username = 'jwttest'
    email = 'jwt@test.com'
    password = 'JwtTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    
    token = response.json()['access_token']
    
    # JWT tokens have 3 parts separated by dots
    parts = token.split('.')
    assert len(parts) == 3, "JWT should have 3 parts (header.payload.signature)"
    
    # Decode without verification to check payload
    SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
    ALGORITHM = os.environ.get('SECRET_ALGORITHM')
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert 'sub' in payload, "Token should contain 'sub' claim"
    assert 'exp' in payload, "Token should contain expiration time"
    
    # Subject should be user_id (as string) - immutable identifier
    user_id_str = payload['sub']
    assert user_id_str.isdigit(), "Subject should be the user's ID (as string)"
    
    # Verify we can fetch the user with this token
    headers = {'Authorization': f'Bearer {token}'}
    user_response = client.get('api/auth/current_user', headers=headers)
    assert user_response.status_code == 200
    assert user_response.json()['email'] == email
    cleanup_account(username)

def test_token_expiration_claim():
    """Test that token contains proper expiration"""
    username = 'exptest'
    email = 'exp@test.com'
    password = 'ExpTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    
    token = response.json()['access_token']
    SECRET_KEY = os.environ.get('AUTH_HASH_KEY')
    ALGORITHM = os.environ.get('SECRET_ALGORITHM')
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Check expiration is in the future
    current_time = time.time()
    assert payload['exp'] > current_time, "Token expiration should be in the future"
    
    # Check it's approximately 30 minutes (within reasonable margin)
    time_diff = payload['exp'] - current_time
    assert 1700 < time_diff < 1900, "Token should expire in approximately 30 minutes"
    cleanup_account(username)

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get('api/auth/current_user')
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with malformed token"""
    headers = {'Authorization': 'Bearer invalidtoken123'}
    response = client.get('api/auth/current_user', headers=headers)
    assert response.status_code == 401

def test_protected_endpoint_with_tampered_token():
    """Test accessing protected endpoint with tampered token"""
    username = 'tampertest'
    email = 'tamper@test.com'
    password = 'TamperTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    
    token = response.json()['access_token']
    
    # Tamper with the token by changing a character
    tampered_token = token[:-5] + 'AAAAA'
    headers = {'Authorization': f'Bearer {tampered_token}'}
    response = client.get('api/auth/current_user', headers=headers)
    assert response.status_code == 401
    cleanup_account(username)

def test_protected_endpoint_with_missing_bearer_prefix():
    """Test accessing protected endpoint without 'Bearer' prefix"""
    username = 'bearertest'
    email = 'bearer@test.com'
    password = 'BearerTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    
    token = response.json()['access_token']
    
    # Send without Bearer prefix
    headers = {'Authorization': token}
    response = client.get('api/auth/current_user', headers=headers)
    assert response.status_code == 401
    cleanup_account(username)

# ============ SECURITY TESTS ============

def test_user_enumeration_timing():
    """Test that response times don't leak info about user existence (basic check)"""
    # This is a basic check - sophisticated timing attacks need more samples
    username = 'timingtest'
    email = 'timing@test.com'
    password = 'TimingTest123!'
    cleanup_account(username)
    
    # Register a user
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Time login attempt with wrong password (user exists)
    start = time.time()
    login_request = LoginRequest(username=username, password='WrongPass123!').model_dump()
    client.post('api/auth/token', json=login_request)
    time_wrong_password = time.time() - start
    
    # Time login attempt with non-existent user
    start = time.time()
    login_request = LoginRequest(username='nonexistentuser123', password='WrongPass123!').model_dump()
    client.post('api/auth/token', json=login_request)
    time_no_user = time.time() - start
    
    # Times should be relatively similar (within 100ms)
    # Note: This is a WEAK test - real timing attacks need statistical analysis
    time_diff = abs(time_wrong_password - time_no_user)
    assert time_diff < 0.1, f"Time difference {time_diff} may indicate timing vulnerability"
    cleanup_account(username)

def test_password_not_in_response():
    """Test that password is never returned in responses"""
    username = 'pwdleaktest'
    email = 'pwdleak@test.com'
    password = 'PwdLeakTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    
    # Get current user
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    user_response = client.get('api/auth/current_user', headers=headers)
    
    # Check password is not in any response
    assert password not in str(login_response.json())
    assert password not in str(user_response.json())
    cleanup_account(username)

def test_sql_injection_in_login():
    """Test SQL injection attempts in login"""
    # These should fail validation, not reach database
    malicious_inputs = [
        "admin' OR '1'='1",
        "admin'--",
        "admin' /*",
        "' OR 1=1--",
        "admin'; DROP TABLE users--"
    ]
    
    for malicious in malicious_inputs:
        login_request = {"username": malicious, "password": "Password123!"}
        response = client.post('api/auth/token', json=login_request)
        # Should either be validation error (422) or unauthorized (401), not 500
        assert response.status_code in [401, 422], f"Failed for input: {malicious}"

# ============ EDGE CASE TESTS ============

def test_multiple_logins_same_user():
    """Test that same user can login multiple times (generate multiple tokens)"""
    username = 'multilogin'
    email = 'multi@test.com'
    password = 'MultiLogin123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login twice
    login_request = LoginRequest(username=username, password=password).model_dump()
    response1 = client.post('api/auth/token', json=login_request)
    response2 = client.post('api/auth/token', json=login_request)
    
    token1 = response1.json()['access_token']
    token2 = response2.json()['access_token']
    
    # Both tokens should work
    headers1 = {'Authorization': f'Bearer {token1}'}
    headers2 = {'Authorization': f'Bearer {token2}'}
    
    assert client.get('api/auth/current_user', headers=headers1).status_code == 200
    assert client.get('api/auth/current_user', headers=headers2).status_code == 200
    cleanup_account(username)

def test_login_with_both_username_and_email():
    """Test login when both username and email are provided (should use username)"""
    username = 'bothfields'
    email = 'both@test.com'
    password = 'BothFields123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login with both fields
    login_request = LoginRequest(username=username, email=email, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 200
    cleanup_account(username)

def test_token_type_is_bearer():
    """Test that token type is always 'bearer'"""
    username = 'typetest'
    email = 'type@test.com'
    password = 'TypeTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    
    data = response.json()
    assert data['token_type'] == 'bearer'
    assert data['token_type'] != 'Bearer'  # Should be lowercase
    cleanup_account(username)

def test_login_special_chars_in_password():
    """Test login with special characters in password"""
    username = 'specialchars'
    email = 'special@test.com'
    password = '!@#$%^&*()_+-=[]{}|;:,.<>?Test123'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login with complex password
    login_request = LoginRequest(username=username, password=password).model_dump()
    response = client.post('api/auth/token', json=login_request)
    assert response.status_code == 200
    cleanup_account(username)
import pytest
from backend.auth.models.register_request import RegisterRequest
from backend.auth.models.login_request import LoginRequest
from fastapi.testclient import TestClient
from backend.app import app
from tests.test_registration import cleanup_account

client = TestClient(app)

# ============ SUCCESSFUL DELETION TESTS ============

def test_delete_own_account():
    """Test that a user can delete their own account"""
    username = 'deletetest'
    email = 'delete@test.com'
    password = 'DeleteTest123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login to get token
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    delete_response = client.delete('api/auth/current_user', headers=headers)
    
    assert delete_response.status_code == 200
    assert 'message' in delete_response.json()
    assert delete_response.json()['username'] == username
    
    # Verify account is actually deleted - login should fail
    login_attempt = client.post('api/auth/token', json=login_request)
    assert login_attempt.status_code == 401

def test_delete_account_cannot_access_after():
    """Test that deleted user's token becomes invalid"""
    username = 'tokentest'
    email = 'token@test.com'
    password = 'TokenTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    client.delete('api/auth/current_user', headers=headers)
    
    # Try to access protected endpoint with old token
    get_user_response = client.get('api/auth/current_user', headers=headers)
    assert get_user_response.status_code == 401

def test_delete_account_response_format():
    """Test that deletion response has correct format"""
    username = 'formattest'
    email = 'format@test.com'
    password = 'FormatTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    delete_response = client.delete('api/auth/current_user', headers=headers)
    
    data = delete_response.json()
    assert 'message' in data
    assert 'username' in data
    assert data['message'] == 'Account deleted successfully'
    assert data['username'] == username

# ============ AUTHENTICATION TESTS ============

def test_delete_without_token():
    """Test that deletion requires authentication"""
    response = client.delete('api/auth/current_user')
    assert response.status_code == 401

def test_delete_with_invalid_token():
    """Test deletion with invalid token"""
    headers = {'Authorization': 'Bearer invalidtoken123'}
    response = client.delete('api/auth/current_user', headers=headers)
    assert response.status_code == 401

def test_delete_with_tampered_token():
    """Test deletion with tampered token"""
    username = 'tamperdelete'
    email = 'tamperdelete@test.com'
    password = 'TamperDelete123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Tamper with token
    tampered_token = token[:-5] + 'AAAAA'
    headers = {'Authorization': f'Bearer {tampered_token}'}
    response = client.delete('api/auth/current_user', headers=headers)
    
    assert response.status_code == 401
    cleanup_account(username)

def test_delete_with_missing_bearer_prefix():
    """Test deletion without 'Bearer' prefix"""
    username = 'bearerdelete'
    email = 'bearerdelete@test.com'
    password = 'BearerDelete123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Send without Bearer prefix
    headers = {'Authorization': token}
    response = client.delete('api/auth/current_user', headers=headers)
    
    assert response.status_code == 401
    cleanup_account(username)

def test_delete_with_expired_token():
    """Test deletion with expired token (if token expiration is short enough to test)"""
    # This would require creating a token with very short expiration
    # For now, we test the invalid credentials path
    username = 'expiredtest'
    email = 'expired@test.com'
    password = 'ExpiredTest123!'
    cleanup_account(username)
    
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Create a fake/malformed token
    headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'}
    response = client.delete('api/auth/current_user', headers=headers)
    assert response.status_code == 401
    cleanup_account(username)

# ============ EDGE CASE TESTS ============

def test_delete_already_deleted_account():
    """Test attempting to delete an account that's already been deleted"""
    username = 'doubleDelete'
    email = 'doubledelete@test.com'
    password = 'DoubleDelete123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    first_delete = client.delete('api/auth/current_user', headers=headers)
    assert first_delete.status_code == 200
    
    # Try to delete again with same token
    second_delete = client.delete('api/auth/current_user', headers=headers)
    assert second_delete.status_code == 401  # User no longer exists

def test_cannot_delete_other_users():
    """Test that a user cannot delete another user's account (implicit - can only delete via own token)"""
    user1 = 'user1delete'
    user2 = 'user2delete'
    email1 = 'user1delete@test.com'
    email2 = 'user2delete@test.com'
    password = 'UsersDelete123!'
    
    cleanup_account(user1)
    cleanup_account(user2)
    
    # Register two users
    register1 = RegisterRequest(username=user1, email=email1, password=password).model_dump()
    register2 = RegisterRequest(username=user2, email=email2, password=password).model_dump()
    client.post('api/auth/register', json=register1)
    client.post('api/auth/register', json=register2)
    
    # Login as user1
    login1 = LoginRequest(username=user1, password=password).model_dump()
    login_response1 = client.post('api/auth/token', json=login1)
    token1 = login_response1.json()['access_token']
    
    # Delete using user1's token (should delete user1, not user2)
    headers = {'Authorization': f'Bearer {token1}'}
    delete_response = client.delete('api/auth/current_user', headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()['username'] == user1
    
    # User2 should still exist and be able to login
    login2 = LoginRequest(username=user2, password=password).model_dump()
    login_response2 = client.post('api/auth/token', json=login2)
    assert login_response2.status_code == 200
    
    cleanup_account(user2)

def test_delete_account_data_cleanup():
    """Test that all user data is removed after deletion"""
    username = 'cleanuptest'
    email = 'cleanup@test.com'
    password = 'CleanupTest123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Verify user exists
    lookup = client.get('api/db/accounts/lookup', params={'identifier': username})
    assert lookup.json()['found'] == True
    
    # Login and delete
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    client.delete('api/auth/current_user', headers=headers)
    
    # Verify user no longer exists
    lookup_after = client.get('api/db/accounts/lookup', params={'identifier': username})
    assert lookup_after.json()['found'] == False

def test_delete_account_can_reregister():
    """Test that after deleting an account, the username/email can be reused"""
    username = 'reregistertest'
    email = 'reregister@test.com'
    password1 = 'FirstPassword123!'
    password2 = 'SecondPassword456!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password1).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password1).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    client.delete('api/auth/current_user', headers=headers)
    
    # Re-register with same username and email but different password
    new_register = RegisterRequest(username=username, email=email, password=password2).model_dump()
    reregister_response = client.post('api/auth/register', json=new_register)
    assert reregister_response.status_code == 200
    
    # Login with new password should work
    new_login = LoginRequest(username=username, password=password2).model_dump()
    new_login_response = client.post('api/auth/token', json=new_login)
    assert new_login_response.status_code == 200
    
    # Old password should NOT work
    old_login = LoginRequest(username=username, password=password1).model_dump()
    old_login_response = client.post('api/auth/token', json=old_login)
    assert old_login_response.status_code == 401
    
    cleanup_account(username)

# ============ SECURITY TESTS ============

def test_delete_no_password_leak():
    """Test that deletion response doesn't leak password hash"""
    username = 'securitytest'
    email = 'security@test.com'
    password = 'SecurityTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    
    # Delete account
    headers = {'Authorization': f'Bearer {token}'}
    delete_response = client.delete('api/auth/current_user', headers=headers)
    
    # Check response doesn't contain password
    response_text = str(delete_response.json())
    assert password not in response_text
    assert 'password' not in delete_response.json()

def test_delete_multiple_concurrent_sessions():
    """Test deleting account when user has multiple active tokens"""
    username = 'multitoken'
    email = 'multitoken@test.com'
    password = 'MultiToken123!'
    cleanup_account(username)
    
    # Register
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    
    # Login twice to get two different tokens
    login_request = LoginRequest(username=username, password=password).model_dump()
    login1 = client.post('api/auth/token', json=login_request)
    login2 = client.post('api/auth/token', json=login_request)
    
    token1 = login1.json()['access_token']
    token2 = login2.json()['access_token']
    
    # Delete with first token
    headers1 = {'Authorization': f'Bearer {token1}'}
    delete_response = client.delete('api/auth/current_user', headers=headers1)
    assert delete_response.status_code == 200
    
    # Second token should now be invalid
    headers2 = {'Authorization': f'Bearer {token2}'}
    get_user_response = client.get('api/auth/current_user', headers=headers2)
    assert get_user_response.status_code == 401

# ============ HTTP METHOD TESTS ============

def test_delete_wrong_http_method():
    """Test that only DELETE method works on the endpoint"""
    username = 'methodtest'
    email = 'method@test.com'
    password = 'MethodTest123!'
    cleanup_account(username)
    
    # Register and login
    register_request = RegisterRequest(username=username, email=email, password=password).model_dump()
    client.post('api/auth/register', json=register_request)
    login_request = LoginRequest(username=username, password=password).model_dump()
    login_response = client.post('api/auth/token', json=login_request)
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Try with POST (should fail - wrong method)
    post_response = client.post('api/auth/current_user', headers=headers)
    assert post_response.status_code == 405  # Method Not Allowed
    
    # Try with PUT (should fail - wrong method)
    put_response = client.put('api/auth/current_user', headers=headers)
    assert post_response.status_code == 405  # Method Not Allowed
    
    cleanup_account(username)

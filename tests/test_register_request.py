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


# SQL Injection Attack Tests
@pytest.mark.parametrize("malicious_username", [
    # Classic SQL injection attempts
    "'; DROP TABLE users; --",
    "admin' OR '1'='1",
    "admin'--",
    "' OR 1=1--",
    "1' OR '1' = '1",
    
    # Comma injection (to break Supabase .or_() queries)
    "test,username.eq.hacker",
    "test,email.eq.admin@admin.com",
    
    # URL/Query parameter injection
    "test?admin=true",
    "test&role=admin",
    
    # Command injection attempts
    "; ls -la",
    "| cat /etc/passwd",
    "$(whoami)",
    
    # XSS attempts (even though this is backend)
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "<img src=x onerror=alert('xss')>",
    
    # Path traversal attempts
    "../../../etc/passwd",
    "..\\..\\windows\\system32",
    
    # NoSQL injection attempts
    "{'$ne': null}",
    "admin' || '1'=='1",
    
    # Unicode/encoding attacks
    "test\x00admin",  # Null byte injection
    "test\r\nadmin",  # CRLF injection
    
    # Special characters that should be blocked
    "test@user",
    "test#user",
    "test$user",
    "test%user",
    "test&user",
    "test*user",
    "test(user)",
    "test[user]",
    "test{user}",
    "test/user",
    "test\\user",
    "test|user",
    "test:user",
    "test;user",
    "test'user",
    'test"user',
    "test<user>",
    "test,user",
    "test.user",
    "test!user",
    "test?user",
    "test+user",
    "test=user",
])
def test_sql_injection_blocked(malicious_username):
    """Test that SQL injection and other malicious inputs are blocked by Pydantic validation"""
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(
            username=malicious_username,
            email="test@test.com",
            password="SecureP@ss123"
        )
    
    # Verify it failed due to username validation
    assert "Username can only contain letters, numbers, and underscores" in str(exc_info.value)


# Additional malicious pattern tests
def test_unicode_emoji_blocked():
    """Test that emoji and unicode characters are blocked"""
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(username="test🔥user", email="test@test.com", password="SecureP@ss123")
    assert "Username can only contain letters, numbers, and underscores" in str(exc_info.value)


def test_spaces_blocked():
    """Test that usernames with spaces are blocked"""
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(username="test user", email="test@test.com", password="SecureP@ss123")
    assert "Username can only contain letters, numbers, and underscores" in str(exc_info.value)


def test_empty_string_blocked():
    """Test that empty usernames are blocked"""
    with pytest.raises(ValidationError):
        RegisterRequest(username="", email="test@test.com", password="SecureP@ss123")


def test_only_special_chars_blocked():
    """Test that usernames with only special characters are blocked"""
    with pytest.raises(ValidationError) as exc_info:
        RegisterRequest(username="!@#$%^&*()", email="test@test.com", password="SecureP@ss123")
    assert "Username can only contain letters, numbers, and underscores" in str(exc_info.value)


def test_valid_with_underscores():
    """Test that valid usernames with underscores are accepted"""
    request = RegisterRequest(username="test_user_123", email="test@test.com", password="SecureP@ss123")
    assert request.username == "test_user_123"


def test_valid_alphanumeric():
    """Test that valid alphanumeric usernames are accepted"""
    request = RegisterRequest(username="testUser123", email="test@test.com", password="SecureP@ss123")
    assert request.username == "testUser123" 

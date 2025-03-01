import jwt
from server import createJWT

def test_create_jwt():
    """Test JWT creation"""
    secret = "test_secret"
    token = createJWT("demo_user", secret, True)
    
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
    
    assert decoded["username"] == "demo_user"
    assert decoded["admin"] is True

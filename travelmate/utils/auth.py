import jwt
import datetime
from passlib.hash import bcrypt
from functools import wraps
from pyramid.httpexceptions import HTTPUnauthorized

SECRET_KEY = "super-secret-key"

def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

def create_jwt(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None

def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request):
        token = request.headers.get('Authorization')
        if not token:
            raise HTTPUnauthorized("Token missing")
        token = token.replace('Bearer ', '')
        payload = decode_jwt(token)
        if not payload:
            raise HTTPUnauthorized("Invalid or expired token")
        request.user_id = payload['user_id']
        return view_func(request)
    return wrapper

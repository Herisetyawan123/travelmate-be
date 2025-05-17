from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from ..models import User
from ..models import SessionLocal
from ..utils.auth import hash_password, verify_password, create_jwt

@view_config(route_name='register', renderer='json', request_method='POST')
def register(request):
    data = request.json_body
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return Response(json_body={'error': 'Incomplete data'}, status=400)

    user = User(username=username, email=email, password=hash_password(password))
    try:
        request.dbsession.add(user)
        request.dbsession.flush()
        request.dbsession.commit() 
    except IntegrityError:
        return Response(json_body={'error': 'Username/email already exists'}, status=400)
    return {'message': 'User registered successfully'}

@view_config(route_name='login', renderer='json', request_method='POST')
def login(request):
    data = request.json_body
    username = data.get('username')
    password = data.get('password')

    user = request.dbsession.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password):
        return Response(json_body={'error': 'Invalid credentials'}, status=401)

    token = create_jwt(user.id)
    return {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'token': token
        }

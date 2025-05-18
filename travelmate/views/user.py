from pyramid.view import view_config
from ..utils.auth import require_auth
from ..helpers.response import api_response
from ..models import User
from ..models import TripMember
from ..utils.auth import hash_password

@view_config(route_name='profile', renderer='json', request_method='GET')
@require_auth
def profile_view(request):
    user_id = request.user_id
    user = request.dbsession.query(User).filter(User.id == user_id).first()
    if not user:
        return api_response(
            status=404,
            message="User not found",
            error="User with the given ID does not exist"
        )
    
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email
    }

    return api_response(
        status=200,
        message="User profile retrieved successfully",
        data=user_data
    )

@view_config(route_name='update_profile', renderer='json', request_method='PUT')
@require_auth
def update_profile(request):
    user_id = request.user_id
    body = request.json_body

    user = request.dbsession.query(User).filter(User.id == user_id).first()
    if not user:
        return api_response(
            status=404,
            message="User not found",
            error="User with the given ID does not exist"
        )

    if 'username' in body:
        user.username = body['username']
    if 'email' in body:
        user.email = body['email']

    request.dbsession.commit()

    return api_response(
        status=200,
        message="User profile updated successfully",
        data={
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

@view_config(route_name='update_password', renderer='json', request_method='PUT')
@require_auth
def update_password(request):
    user_id = request.user_id
    body = request.json_body

    user = request.dbsession.query(User).filter(User.id == user_id).first()
    if not user:
        return api_response(
            status=404,
            message="User not found",
            error="User with the given ID does not exist"
        )

    user.password = hash_password(body['new_password'])
    request.dbsession.commit()

    return api_response(
        status=200,
        message="Password updated successfully"
    )

@view_config(route_name='get_all_users', request_method='GET', renderer='json')
@require_auth
def get_all_users(request):
    try:
        users = request.dbsession.query(User).all()
        result = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
        } for user in users]

        return api_response(data=result)

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to fetch users")

@view_config(route_name='get_non_members', request_method='GET', renderer='json')
@require_auth
def get_non_trip_members(request):
    try:
        trip_id = request.params.get('trip_id')
        if not trip_id:
            return api_response(status=400, message="trip_id is required")

        # Subquery: ambil user_id yang sudah jadi member di trip ini
        subquery = request.dbsession.query(TripMember.user_id).filter_by(trip_id=trip_id).subquery()

        # Ambil user yang BUKAN member trip ini
        users = request.dbsession.query(User).filter(~User.id.in_(subquery)).all()

        result = [{
            "id": user.id,
            "username": user.username,
            "email": user.email,
        } for user in users]

        return api_response(data=result)

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to fetch non-members")

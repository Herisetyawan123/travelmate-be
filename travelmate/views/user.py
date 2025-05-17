from pyramid.view import view_config
from ..utils.auth import require_auth
from ..helpers.response import api_response
from ..models import User

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
from pyramid.view import view_config
from ..utils.auth import require_auth
from ..models import Trip, TripMember
from ..helpers.response import api_response
from datetime import datetime

@view_config(route_name='home', renderer='json')
def home_view(request):
    return {'message': 'TravelMate API is running'}

@view_config(route_name='dashboard', renderer='json')
@require_auth
def dashboard_view(request):
    user_id = request.user_id

    owner_trip = request.dbsession.query(Trip).filter_by(owner_id=user_id).all()
    member_trip = request.dbsession.query(Trip).join(TripMember).filter_by(user_id=user_id).all()

    trips = owner_trip + member_trip

    total_upcoming_trip = request.dbsession.query(Trip).filter_by(owner_id=user_id).filter(Trip.start_date > datetime.now()).count() + request.dbsession.query(Trip).join(TripMember).filter_by(user_id=user_id).filter(Trip.start_date > datetime.now()).count()
    total_completed_trip = request.dbsession.query(Trip).filter_by(owner_id=user_id).filter(Trip.end_date < datetime.now()).count() + request.dbsession.query(Trip).join(TripMember).filter_by(user_id=user_id).filter(Trip.end_date < datetime.now()).count()
    
    return api_response(
        status=200,
        message="Dashboard data retrieved successfully",
        data={
            "total_trips": len(trips),
            "upcoming_trips": total_upcoming_trip,
            "completed_trips": total_completed_trip,
        }
    )
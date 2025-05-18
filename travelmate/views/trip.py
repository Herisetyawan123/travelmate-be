from pyramid.view import view_config
from datetime import datetime
from ..models import Trip
from ..models import TripMember
from ..models import User, Itinerary, Activity
from ..helpers.response import api_response
from ..utils.auth import require_auth
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from cgi import FieldStorage
import uuid
from decimal import Decimal
from ..config import HOST

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'uploads'))

@view_config(route_name='create_trip', request_method='POST', renderer='json')
@require_auth
def create_trip(request):
    from datetime import datetime, timedelta
    from decimal import Decimal
    from cgi import FieldStorage

    data = request.POST

    try:
        # Validasi & parsing tanggal
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        if end_date < start_date:
            return api_response(status=400, message="End date cannot be before start date")

        # Handle file upload (thumbnail)
        thumbnail_file = data.get('thumbnail')
        thumbnail_filename = None
        if isinstance(thumbnail_file, FieldStorage) and hasattr(thumbnail_file, 'file'):
            original_filename = secure_filename(thumbnail_file.filename)
            ext = os.path.splitext(original_filename)[1]
            renamed_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(UPLOAD_DIR, renamed_filename)

            with open(file_path, 'wb') as f:
                f.write(thumbnail_file.file.read())
            thumbnail_filename = f"/uploads/{renamed_filename}"

        # Buat Trip
        trip = Trip(
            name=data.get('name'),
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            is_private=data.get('is_private', 'false').lower() == 'true',
            destination=data.get('destination'),
            thumbnail=thumbnail_filename,
            owner_id=request.user_id,
            initial_budget=Decimal(data.get('initial_budget') or 0)
        )
        request.dbsession.add(trip)
        request.dbsession.flush()  # Untuk dapatkan trip.id

        # Tambahkan TripMember (owner)
        trip_member = TripMember(
            trip_id=trip.id,
            user_id=request.user_id,
            role='owner'
        )
        request.dbsession.add(trip_member)

        # Auto generate Itinerary berdasarkan rentang tanggal
        current_date = start_date
        day_number = 1
        while current_date <= end_date:
            itinerary = Itinerary(
                trip_id=trip.id,
                day_number=day_number,
                date=current_date
            )
            request.dbsession.add(itinerary)
            current_date += timedelta(days=1)
            day_number += 1

        request.dbsession.commit()

        return api_response(
            message="Trip created successfully",
            status=201,
            data={
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "initial_budget": str(trip.initial_budget),
                "start_date": trip.start_date.isoformat(),
                "end_date": trip.end_date.isoformat(),
                "is_private": trip.is_private,
                "thumbnail": HOST + trip.thumbnail if trip.thumbnail else None
            }
        )

    except Exception as e:
        request.dbsession.rollback()
        return api_response(status=500, message="Failed to create trip", error=str(e))


@view_config(route_name='get_trips', request_method='GET', renderer='json')
@require_auth
def get_trips(request):
    try:
        user_id = request.user_id
        trip_memberships = request.dbsession.query(TripMember).filter_by(user_id=user_id).all()
        trip_ids = [tm.trip_id for tm in trip_memberships]

        trips = request.dbsession.query(Trip).filter(Trip.id.in_(trip_ids)).all()

        result = []
        for t in trips:
            members_data = [{
                "user_id": member.user_id,
                "name": member.user.username,
                "role": member.role,
            } for member in t.members]
            print("members_data", members_data)

            result.append({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "initial_budget": str(t.initial_budget),
                "destination": t.destination,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "thumbnail": HOST+t.thumbnail,
                "members": members_data
            })


        return api_response(data=result)

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to fetch trips")


@view_config(route_name='get_trip', request_method='GET', renderer='json')
@require_auth
def get_trip(request):
    trip_id = request.matchdict.get('id')
    try:
        trip = request.dbsession.query(Trip).filter_by(id=trip_id, owner_id=request.user_id).first()
        if not trip:
            return api_response(status=404, error="Trip not found")

        # Serialisasi members
        members_data = [{
            "user_id": member.user_id,
            "username": member.user.username if member.user else None,
            "role": member.role
        } for member in trip.members]

        # Serialisasi comments
        comments_data = [{
            "id": comment.id,
            "user_id": comment.user_id,
            "username": comment.user.username if comment.user else None,
            "content": comment.content,
            "created_at": comment.created_at.isoformat() if comment.created_at else None
        } for comment in trip.comments]

        result = {
            "id": trip.id,
            "name": trip.name,
            "description": trip.description,
            "destination": trip.destination,
            "start_date": trip.start_date.isoformat(),
            "end_date": trip.end_date.isoformat(),
            "is_private": trip.is_private,
            "thumbnail": HOST+trip.thumbnail,
            "members": members_data,
            "comments": comments_data,
        }

        return api_response(data=result)

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to fetch trip")


@view_config(route_name='update_trip', request_method='PUT', renderer='json')
@require_auth
def update_trip(request):
    trip_id = request.matchdict.get('id')
    data = request.POST

    try:
        thumbnail_file = request.POST.get('thumbnail')

        thumbnail_filename = None
        if isinstance(thumbnail_file, FieldStorage) and hasattr(thumbnail_file, 'file'):
            original_filename = secure_filename(thumbnail_file.filename)
            ext = os.path.splitext(original_filename)[1]
            renamed_filename = f"{uuid.uuid4().hex}{ext}" 
            file_path = os.path.join(UPLOAD_DIR, renamed_filename)

            with open(file_path, 'wb') as f:
                f.write(thumbnail_file.file.read())
            thumbnail_filename = f"/uploads/{renamed_filename}"

        trip = request.dbsession.query(Trip).filter_by(id=trip_id, owner_id=request.user_id).first()
        if not trip:
            return api_response(status=404, error="Trip not found")

        trip.name = data.get('name', trip.name)
        trip.description = data.get('description', trip.description)
        trip.start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d') if data.get('start_date') else trip.start_date
        trip.end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d') if data.get('end_date') else trip.end_date
        trip.thumbnail = thumbnail_filename
        trip.initial_budget = Decimal(data.get('initial_budget') or trip.initial_budget)

        request.dbsession.flush()
        return api_response(message="Trip updated successfully", data={
            "id": trip.id,
            "name": trip.name,
            "description": trip.description,
            "start_date": trip.start_date.isoformat(),
            "end_date": trip.end_date.isoformat(),
            "is_private": trip.is_private,
            "thumbnail": HOST+trip.thumbnail
        })

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to update trip")


@view_config(route_name='delete_trip', request_method='DELETE', renderer='json')
@require_auth
def delete_trip(request):
    trip_id = request.matchdict.get('id')
    try:
        trip = request.dbsession.query(Trip).filter_by(id=trip_id, owner_id=request.user_id).first()
        if not trip:
            return api_response(status=404, error="Trip not found")

        request.dbsession.delete(trip)
        request.dbsession.flush()
        request.dbsession.commit()
        return api_response(message="Trip deleted successfully")

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to delete trip")

@view_config(route_name='invite_member', request_method='POST', renderer='json')
@require_auth
def invite_member(request):
    try:
        data = request.json_body
        trip_id = data.get('trip_id')
        user_id = data.get('user_id')

        trip = request.dbsession.query(Trip).filter_by(id=trip_id, owner_id=request.user_id).first()
        if not trip:
            return api_response(status=404, message="Trip not found")

        user = request.dbsession.query(User).filter_by(id=user_id).first()
        if not user:
            return api_response(status=404, message="User not found")

        existing = request.dbsession.query(TripMember).filter_by(trip_id=trip_id, user_id=user_id).first()
        if existing:
            return api_response(status=400, message="User already a member of this trip")

        member = TripMember(trip_id=trip_id, user_id=user_id, role='member')
        request.dbsession.add(member)
        request.dbsession.commit()

        return api_response(message="User invited to trip", data={"member_id": member.id})

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to invite member")

@view_config(route_name='get_itinerary_by_trip', request_method='GET', renderer='json')
@require_auth
def get_itinerary_by_trip(request):
    trip_id = request.matchdict.get('trip_id')

    try:
        itineraries = request.dbsession.query(Itinerary).filter_by(trip_id=trip_id).order_by(Itinerary.id).all()
        result = []

        for itinerary in itineraries:
            result.append({
                'id': itinerary.id,
                'day_number': itinerary.day_number,
                'activities': [
                    {
                        'id': activity.id,
                        'title': activity.title,
                        'description': activity.description,
                        'order': activity.order,
                        'time': activity.time.isoformat() if activity.time else None,
                        'category': activity.category,
                        'location': activity.location,

                    }
                    for activity in itinerary.activities
                ]
            })

        return api_response(
            status=200,
            message="Itinerary retrieved successfully",
            data=result
        )

    except Exception as e:
        return api_response(status=500, message="Failed to fetch itinerary", error=str(e))


@view_config(route_name='add_activity', request_method='POST', renderer='json')
@require_auth
def add_activity(request):
    from decimal import Decimal
    data = request.json_body
    itinerary_id = request.matchdict.get('itinerary_id')

    try:
        title = data.get('title')
        description = data.get('description')
        order = int(data.get('order'))
        time = data.get('time')
        category = data.get('category')
        location = data.get('location')

        if not title:
            return api_response(status=400, message="Title is required")

        activity = Activity(
            itinerary_id=itinerary_id,
            title=title,
            description=description,
            order=order,
            time=time,
            category=category,
            location=location,
        )
        request.dbsession.add(activity)
        request.dbsession.commit()

        return api_response(
            status=201,
            message="Activity added successfully",
            data={
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'order': activity.order,
                'time': activity.time.isoformat() if activity.time else None,
                'category': activity.category,
                'location': activity.location,
            }
        )

    except Exception as e:
        request.dbsession.rollback()
        return api_response(status=500, message="Failed to add activity", error=str(e))

@view_config(route_name='bulk_update_activities', request_method='PUT', renderer='json')
def bulk_update_activities(request):
    data = request.json_body

    ids = [item['id'] for item in data]
    print("ids", ids)
    dbsession = request.dbsession
    activities = dbsession.query(Activity).filter(Activity.id.in_(ids)).all()
    # activity_map = {act.id: act for act in activities}
    activity_map = {act.id: act for act in activities}
    for item in data:
            act = activity_map.get(item['id'])
            # print("act", act.id)
            if act:
                act.order = item['order']
    dbsession.commit()
    return api_response(
        status=200,
        message="Bulk update activities",
        data="activities"
    )

@view_config(route_name='delete_activity', request_method='DELETE', renderer='json')
def delete_activity(request):
    activity_id = request.matchdict.get('id')
    print("activity_id", activity_id)
    try:
        activity = request.dbsession.query(Activity).filter_by(id=activity_id).first()
        if not activity:
            return api_response(status=404, message="Activity not found")

        request.dbsession.delete(activity)
        request.dbsession.commit()

        return api_response(message="Activity deleted successfully")    
    except Exception as e:
        request.dbsession.rollback()
        return api_response(status=500, message="Failed to delete activity", error=str(e))
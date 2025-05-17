from pyramid.view import view_config
from datetime import datetime
from ..models import Trip
from ..models import TripMember
from ..helpers.response import api_response
from ..utils.auth import require_auth
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from cgi import FieldStorage
import uuid
from ..config import HOST

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..', 'uploads'))

@view_config(route_name='create_trip', request_method='POST', renderer='json')
@require_auth
def create_trip(request):
    data = request.POST

    try:
        # Ambil file
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

        trip = Trip(
            name=data.get('name'),
            description=data.get('description'),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d'),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d'),
            is_private=data.get('is_private').lower() == 'true',
            thumbnail=thumbnail_filename,
            owner_id=request.user_id
        )
        request.dbsession.add(trip)
        request.dbsession.flush()

        trip_member = TripMember(
            trip_id=trip.id,
            user_id=request.user_id,
            role='owner'
        )
        request.dbsession.add(trip_member)

        request.dbsession.commit()

        return api_response(
            message="Trip created successfully",
            status=201,
            data={
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "start_date": trip.start_date.isoformat(),
                "end_date": trip.end_date.isoformat(),
                "is_private": trip.is_private,
                "thumbnail": HOST+trip.thumbnail
            }
            )

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to create trip")


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
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "thumbnail": t.thumbnail,
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
            "start_date": trip.start_date.isoformat(),
            "end_date": trip.end_date.isoformat(),
            "is_private": trip.is_private,
            "thumbnail": trip.thumbnail,
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

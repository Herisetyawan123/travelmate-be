from pyramid.view import view_config
from ..models import Destination

@view_config(route_name='get_destination', renderer='json')
def get_destination(request):
    trip_id = request.matchdict.get('id')
    db = request.dbsession
    destination = db.query(Destination).filter(trip_id == trip_id).all()

    destination = [
        {
            'id': d.id,
            'name': d.name,
            'description': d.description,
            'location': d.location,
            'latitude': d.latitude,
            'longitude': d.longitude,
            'address': d.address,

            'created_at': d.created_at.isoformat(),
            'updated_at': d.updated_at.isoformat()
        } for d in destination
    ]

    return {
        'status': 200,
        'message': 'Success',
        'data': destination
    }

@view_config(route_name='create_destination', renderer='json')
def create_destination(request):
    body = request.json_body
    trip_id = body.get('trip_id')
    name = body.get('name')
    description = body.get('description')
    location = body.get('location')
    latitude = body.get('latitude')
    longitude = body.get('longitude')
    address = body.get('address')
    notes = body.get('notes')
    

    destination = Destination(
        trip_id=trip_id,
        name=name,
        description=description,
        location=location,
        latitude=latitude,
        longitude=longitude,
        address=address,
        notes=notes
    )

    request.dbsession.add(destination)
    request.dbsession.flush()
    request.dbsession.commit()

    return {
        'status': 201,
        'message': 'Destination created successfully',
        'data': {
            'id': destination.id,
            'trip_id': destination.trip_id,
            'name': destination.name,
            'description': destination.description,
            'location': destination.location,
            'latitude': destination.latitude,
            'longitude': destination.longitude,
            'address': destination.address,
            'notes': destination.notes,

            'created_at': destination.created_at.isoformat(),
            'updated_at': destination.updated_at.isoformat()
        }
    }

from pyramid.config import Configurator
from pyramid.events import NewRequest
from .models import engine, Base
from .models import SessionLocal

def dbsession_handler(event):
    request = event.request
    request.dbsession = SessionLocal()

def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        })
    event.request.add_response_callback(cors_headers)

def main(global_config, **settings):
    config = Configurator(settings=settings)

    # Tambahkan subscriber untuk DB session dan CORS
    config.add_subscriber(dbsession_handler, NewRequest)
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    # Tambahkan static view untuk folder uploads
    config.add_static_view(name='uploads', path='../uploads', cache_max_age=3600)


    # Buat tabel
    Base.metadata.create_all(bind=engine)


    config.add_route('options', '/{path:.*}', request_method='OPTIONS')\

    # Definisi route utama
    config.add_route('home', '/')
    config.add_route('register', '/api/register')
    config.add_route('login', '/api/login')
    config.add_route('profile', '/api/profile')
    config.add_route('get_all_users', '/api/users')
    config.add_route('delete_activity', '/api/activities/delete/{id}')

    # Trip routes
    config.add_route('get_trips', '/api/trips')
    config.add_route('get_non_members', '/api/trips/non-members')
    config.add_route('create_trip', '/api/trips/store')
    config.add_route('invite_member', '/api/trips/member')
    config.add_route('get_trip', '/api/trips/{id}')
    config.add_route('update_trip', '/api/trips/{id}/edit')
    config.add_route('delete_trip', '/api/trips/{id}/delete')
    config.add_route('get_itinerary_by_trip', '/api/trips/{trip_id}/itinerary')
    config.add_route('add_activity', '/api/itinerary/{itinerary_id}/activities')
    config.add_route('bulk_update_activities', '/api/activities/bulk-update')


    # comment routes
    config.add_route('add_comment', '/api/trips/{id}/comments')
    config.add_route('get_comments', '/api/trips/{id}/comments/all')

    config.scan('travelmate.views')

    return config.make_wsgi_app()

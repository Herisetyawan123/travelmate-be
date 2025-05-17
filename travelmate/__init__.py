from pyramid.config import Configurator
from pyramid.events import NewRequest
from .models import engine, Base
from .models import SessionLocal


def dbsession_handler(event):
    request = event.request
    request.dbsession = SessionLocal()

def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_static_view(name='uploads', path='../uploads', cache_max_age=3600)
    config.add_subscriber(dbsession_handler, NewRequest)

    Base.metadata.create_all(bind=engine)
    
    # Tambahkan route di sini nanti
    config.add_route('home', '/')
    config.add_route('register', '/api/register')
    config.add_route('login', '/api/login')
    config.add_route('profile', '/api/profile')

    # Route untuk Trip
    config.add_route('get_trips', '/api/trips')
    config.add_route('create_trip', '/api/trips/store')
    config.add_route('get_trip', '/api/trips/{id}')
    config.add_route('update_trip', '/api/trips/{id}/edit')
    config.add_route('delete_trip', '/api/trips/{id}/delete')
    
    config.scan('travelmate.views')  # Mendeteksi @view_config secara otomatis

    return config.make_wsgi_app()
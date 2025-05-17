from pyramid.config import Configurator
from pyramid.events import NewRequest
from .models import engine, Base
from .models import SessionLocal

def dbsession_handler(event):
    request = event.request
    request.dbsession = SessionLocal()

def main(global_config, **settings):
    config = Configurator(settings=settings)

    config.add_subscriber(dbsession_handler, NewRequest)

    Base.metadata.create_all(bind=engine)
    
    # Tambahkan route di sini nanti
    config.add_route('home', '/')
    config.add_route('register', '/register')
    config.add_route('login', '/login')
    config.add_route('profile', '/profile')
    
    config.scan('travelmate.views')  # Mendeteksi @view_config secara otomatis

    return config.make_wsgi_app()
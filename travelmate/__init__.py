from pyramid.config import Configurator
from .models import engine, Base

def main(global_config, **settings):
    config = Configurator(settings=settings)

    Base.metadata.create_all(bind=engine)
    
    # Tambahkan route di sini nanti
    config.add_route('home', '/')
    
    config.scan('travelmate.views')  # Mendeteksi @view_config secara otomatis

    return config.make_wsgi_app()
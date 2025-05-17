from pyramid.view import view_config

@view_config(route_name='home', renderer='json')
def home_view(request):
    return {'message': 'TravelMate API is running'}

from pyramid.view import view_config

@view_config(route_name='options', request_method='OPTIONS', renderer='json')
def options_view(request):
    return {}

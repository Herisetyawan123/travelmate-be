from pyramid.view import view_config
from ..models import TripTodo
from ..utils.notify_socket import notify

@view_config(route_name='get_trip_todos', renderer='json', request_method='GET')
def get_trip_todos(request):
    trip_id = request.params.get('trip_id')
    query = request.dbsession.query(TripTodo)
    if trip_id:
        query = query.filter(TripTodo.trip_id == trip_id)
    todos = query.all()

    return {
        'status': 200,
        'message': 'Success',
        'data': [
            {
                'id': todo.id,
                'trip_id': todo.trip_id,
                'category': todo.category,
                'description': todo.description,
                'status': todo.status
            } for todo in todos
        ]
    }

@view_config(route_name='create_trip_todo', renderer='json', request_method='POST')
def create_trip_todo(request):
    body = request.json_body
    trip_id = body.get('trip_id')
    category = body.get('category')
    description = body.get('description')

    if not trip_id or not category or not description:
        return {
            'status': 400,
            'message': 'Missing required fields'
        }

    new_todo = TripTodo(
        trip_id=trip_id,
        category=category,
        description=description,
        status="not_yet"
    )
    request.dbsession.add(new_todo)
    request.dbsession.flush()
    request.dbsession.commit()
    notify("todo_created")

    return {
        'status': 201,
        'message': 'Trip todo created successfully',
        'data': {
            'id': new_todo.id,
            'trip_id': new_todo.trip_id,
            'category': new_todo.category,
            'description': new_todo.description,
            'status': new_todo.status
        }
    }

@view_config(route_name='update_trip_todo', renderer='json', request_method='PUT')
def update_trip_todo(request):
    try:
        todo_id = request.matchdict.get("id")
        body = request.json_body
        todo = request.dbsession.query(TripTodo).filter(TripTodo.id == todo_id).first()

        if not todo:
            return {
                "status": 404,
                "message": "Trip todo not found"
            }

        if 'status' in body:
            todo.status = body['status']

        request.dbsession.commit()
        notify("todo_updated")

        return {
            "status": 200,
            "message": "Trip todo updated successfully",
            "data": {
                "id": todo.id,
                "trip_id": todo.trip_id,
                "category": todo.category,
                "description": todo.description,
                "status": todo.status
            }
        }
    except Exception as e:
        return {
            "status": 500,
            "message": "Failed to update trip todo",
            "error": str(e)
        }

@view_config(route_name="delete_trip_todo", renderer="json", request_method="DELETE")
def delete_trip_todo(request):
    todo_id = request.matchdict.get("id")
    todo = request.dbsession.query(TripTodo).filter(TripTodo.id == todo_id).first()

    if not todo:
        return {
            "status": 404,
            "message": "Trip todo not found"
        }

    request.dbsession.delete(todo)
    request.dbsession.commit()
    notify("todo_deleted")
    return {
        "status": 200,
        "message": "Trip todo deleted successfully"
    }
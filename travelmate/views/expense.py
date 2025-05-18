from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from ..models import Expense
import json
from datetime import datetime

@view_config(route_name='get_expenses', renderer='json', request_method='GET')
def get_expenses(request):
    try:
        trip_id = request.params.get('trip_id')
        query = request.dbsession.query(Expense)

        if trip_id:
            query = query.filter(Expense.trip_id == int(trip_id))

        expenses = query.all()

        data = [{
            'id': expense.id,
            'trip_id': expense.trip_id,
            'name': expense.name,
            'amount': expense.amount,
            'date': expense.date.isoformat() if expense.date else None,
            'category': expense.category,
            'notes': expense.notes
        } for expense in expenses]

        return {
            'status': 200,
            'message': 'Expenses retrieved successfully',
            'data': data
        }

    except SQLAlchemyError as e:
        return Response(
            json.dumps({
                'status': 500,
                'message': 'Failed to retrieve expenses',
                'error': str(e)
            }),
            content_type='application/json',
            status=500
        )

@view_config(route_name='create_expense', renderer='json', request_method='POST')
def create_expense(request):
    try:
        body = request.json_body

        # Validasi input wajib
        required_fields = ['trip_id', 'name', 'amount']
        for field in required_fields:
            if field not in body:
                return Response(
                    json.dumps({
                        'status': 400,
                        'message': f'Missing required field: {field}'
                    }),
                    content_type='application/json',
                    status=400
                )

        # Buat objek Expense baru
        expense = Expense(
            trip_id=body['trip_id'],
            name=body['name'],
            amount=body['amount'],
            date=datetime.strptime(body['date'], '%Y-%m-%d').date() if 'date' in body and body['date'] else None,
            category=body.get('category'),
            notes=body.get('notes')
        )

        request.dbsession.add(expense)
        request.dbsession.flush()  # untuk mendapatkan ID yang baru dibuat
        request.dbsession.commit()
        return {
            'status': 200,
            'message': 'Expense created successfully',
            'data': {
                'id': expense.id,
                'trip_id': expense.trip_id,
                'name': expense.name,
                'amount': expense.amount,
                'date': expense.date.isoformat() if expense.date else None,
                'category': expense.category,
                'notes': expense.notes
            }
        }

    except SQLAlchemyError as e:
        return Response(
            json.dumps({
                'status': 500,
                'message': 'Failed to create expense',
                'error': str(e)
            }),
            content_type='application/json',
            status=500
        )
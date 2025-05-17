from pyramid.view import view_config
from ..helpers.response import api_response
from ..utils.auth import require_auth
from ..models import Comment
from ..models import Trip

@view_config(route_name='add_comment', request_method='POST', renderer='json')
@require_auth
def add_comment(request):
    try:
        trip_id = request.matchdict.get('id')
        user_id = request.user_id
        comment_text = request.json_body.get('comment')

        if not comment_text:
            return api_response(status=400, error="Comment cannot be empty")

        # Validasi apakah trip-nya ada
        trip = request.dbsession.query(Trip).filter_by(id=trip_id).first()
        if not trip:
            return api_response(status=404, error="Trip not found")

        comment = Comment(
            trip_id=trip_id,
            user_id=user_id,
            content=comment_text
        )

        request.dbsession.add(comment)
        request.dbsession.commit()

        return api_response(message="Comment added successfully", data={
            "id": comment.id,
            "comment": comment.content,
            "created_at": comment.created_at.isoformat()
        })

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to add comment")

@view_config(route_name='get_comments', request_method='GET', renderer='json')
@require_auth
def get_comments(request):
    try:
        trip_id = request.matchdict.get('id')

        comments = (
            request.dbsession.query(Comment)
            .filter_by(trip_id=trip_id)
            .order_by(Comment.created_at.desc())
            .all()
        )

        result = [{
            "id": c.id,
            "user_id": c.user_id,
            "username": c.user.username if c.user else None,
            "comment": c.content,
            "created_at": c.created_at.isoformat()
        } for c in comments]

        return api_response(data=result)

    except Exception as e:
        return api_response(status=500, message=str(e), error="Failed to fetch comments")

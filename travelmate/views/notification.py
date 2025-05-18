from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm import Session
import json
from ..models import Notification
from ..utils.auth import require_auth

@view_config(route_name='notifications', renderer='json', request_method='GET')
@require_auth
def get_notifications(request):
    user_id = request.user_id
    db: Session = request.dbsession
    notifications = db.query(Notification).filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()
    return [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "read": n.read,
        "createdAt": n.created_at.isoformat(),
    } for n in notifications]

@view_config(route_name='mark_notification_read', renderer='json', request_method='POST')
def mark_notification_read(request):
    notif_id = int(request.matchdict['id'])
    db: Session = request.dbsession
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.read = True
        db.flush()
        return {"status": "success", "message": "Notification marked as read."}
    return Response(json.dumps({"status": "error", "message": "Notification not found."}), status=404)

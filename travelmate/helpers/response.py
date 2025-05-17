from webob import Response
import json

def api_response(data=None, message="", error="", status=200):
    payload = {
        "status": status,
        "message": message,
        "error": error,
        "data": data if data is not None else []
    }
    return Response(
        body=json.dumps(payload),
        status=status,
        content_type="application/json; charset=utf-8"
    )

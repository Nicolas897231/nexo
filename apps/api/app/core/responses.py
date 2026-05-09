from app.middleware.request_context import get_request_id


def ok(data=None, **extra) -> dict:
    payload = {"success": True, "data": data, "meta": {"request_id": get_request_id()}}
    payload.update(extra)
    return payload

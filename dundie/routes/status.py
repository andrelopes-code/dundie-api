from fastapi import HTTPException


def get_status(message: str):
    return {
        'description': message,
        'content': {'application/json': {'example': {'detail': 'detail'}}},
    }


def exp401(detail: str, scheme: str = 'Bearer') -> HTTPException:
    return HTTPException(401, detail, headers={'WWW-Authenticate': scheme})


def exp403(detail: str, scheme: str = 'Bearer') -> HTTPException:
    return HTTPException(403, detail, headers={'WWW-Authenticate': scheme})

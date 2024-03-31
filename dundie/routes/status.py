def get_status(message: str):
    return {
        "description": message,
        "content": {"application/json": {"example": {"detail": 'detail'}}},
    }

from sqlmodel import Session, select
from dundie.models import User, LikedPosts


def check_post_is_liked(
    user: User,
    post_id: int,
    session: Session,
    notbool: bool = False
) -> bool | LikedPosts:

    condition = (
        (LikedPosts.post_id == post_id)
        & (LikedPosts.user_id == user.id)
    )
    stmt = select(LikedPosts).where(condition)
    is_liked = session.exec(stmt).first()

    if is_liked and notbool:
        return is_liked

    return bool(is_liked)

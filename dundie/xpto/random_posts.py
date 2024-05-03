from random import randint
from fastapi import HTTPException
from sqlmodel import select
from dundie.db import Session, engine
from dundie.models import User, Post
from datetime import datetime, timedelta

RANDOM_WORDS = (
    "posuere sollicitudin aliquam ultrices sagittis orci a scelerisque purus semper eget duis at tellus at urna condimentum mattis pellentesque id nibh tortor id aliquet lectus proin nibh nisl condimentum id venenatis a condimentum vitae sapien pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas sed tempus urna et pharetra pharetra massa massa ultricies mi quis hendrerit dolor magna eget est lorem ipsum dolor sit amet consectetur adipiscing elit pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas integer eget aliquet nibh praesent tristique magna sit amet purus gravida quis blandit turpis cursus in hac habitasse platea dictumst quisque sagittis purus sit amet volutpat consequat mauris nunc congue nisi vitae suscipit tellus mauris a diam maecenas sed enim ut sem viverra aliquet eget sit amet tellus cras adipiscing enim eu turpis egestas pretium aenean pharetra magna ac placerat vestibulum lectus mauris ultrices eros in cursus turpis massa tincidunt dui ut ornare lectus sit amet est placerat in egestas erat imperdiet sed euismod nisi porta lorem mollis aliquam ut porttitor leo a diam sollicitudin tempor id eu nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit amet risus nullam eget felis eget nunc lobortis mattis aliquam faucibus purus in massa tempor nec feugiat nisl pretium fusce id velit ut tortor pretium viverra suspendisse potenti nullam ac tortor vitae purus faucibus ornare suspendisse sed nisi lacus sed viverra tellus in hac habitasse platea dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim cras tincidunt lobortis".split()
)


def get_random_post_content():
    return " ".join([RANDOM_WORDS[randint(0, len(RANDOM_WORDS) - 1)] for _ in range(0, randint(6, 50))])


def get_random_date():
    initial = datetime(2023, 1, 1, 0, 0, 0)
    final = datetime.now()
    diff = final - initial
    
    return initial + timedelta(seconds=randint(0, int(diff.total_seconds())))


def create_random_posts(max_per_user=30):
    with Session(engine) as session:
        stmt = select(User.username).where(User.is_active == True)
        usernames = session.exec(stmt).all()

        posts = []

        for username in usernames:
            
            # 50% chance of not creating a post
            if randint(0, 1) == 0:
                continue
            
            user = session.exec(select(User).where(User.username == username)).first()
            
            for _ in range(0, randint(1, max_per_user)):
                posts.append(
                    Post(
                        user_id=user.id,
                        content=get_random_post_content(),
                        likes=0,
                        date=get_random_date()
                    )
                )
            
        
        try:
            session.add_all(posts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}

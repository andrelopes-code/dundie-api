from random import randint, choice
from fastapi import HTTPException
from sqlmodel import select
from dundie.db import engine, Session
from dundie.models import User, Post, LikedPosts
from datetime import datetime, timedelta
from dundie.routes.post import like_post



def random_like_posts(posts_per_user=100, max_posts=500):
    with Session(engine) as session:
        stmt = select(User.username).where(User.is_active == True)
        usernames = session.exec(stmt).all()
        
        stmt = select(Post.id).limit(max_posts)
        post_ids = session.exec(stmt).all()

        for username in usernames:
            
            user = session.exec(select(User).where(User.username == username)).first()
            
            for _ in range(0, randint(1, posts_per_user)):
                
                post_to_like = choice(post_ids)
                condition = (LikedPosts.post_id == post_to_like) & (LikedPosts.user_id == user.id)
                stmt = select(LikedPosts).where(condition)
                has_liked = session.exec(stmt).first()
                if has_liked:
                    continue
                
                post = session.exec(select(Post).where(Post.id == post_to_like)).first()
                if not post:
                    continue

                post_liked = LikedPosts(post_id=post_to_like, user_id=user.id)
                post.likes += 1
                session.add(post_liked)
                session.add(post)

            try:
                session.commit()
            except Exception as e:
                session.rollback()
                raise HTTPException(500, e.orig.diag.message_detail)
            
    return {"detail": "successful"}
            
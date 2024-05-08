import random
from dundie.db import engine
from sqlmodel import Session
from .constants import NAMES
from dundie.config import settings
from dundie.controllers import create_user_and_balance

departments = ["marketing", "sales", "humanresources", "finance", "operations", "it", "logistics"]
default_password = "@Dundie2024!"
names = NAMES

def generate_username(name):
    username = name.lower().replace(" ", "")
    return username


def generate_email(username):
    domains = ["outlook.com", "email.com", "mail.com"]
    return username + "@" + random.choice(domains)


def create_private_users(session):
    
    private_users = [
        {
            "name": "Admin",
            "username": "admin",
            "email": "admin@adm",
            "password": settings.security.ADMIN_PASS,
            "dept": "management",
            "private": True,
            "currency": "USD"
        },
        {
            "name": "Points Delivery Man",
            "username": "pointsdeliveryman",
            "email": "deliveryman@points",
            "password": settings.security.DELIVERY_PASS,
            "dept": "management",
            "private": True,
            "currency": "USD"
        },
        {
            "name": "André Lopes",
            "username": "andrelps",
            "email": "andrelps@gmail.com",
            "password": "38902840",
            "dept": "management",
            "currency": "USD"
        },
    ]
    
    for user in private_users:
        
        create_user_and_balance(user, session)


def create_test_users():
    with Session(engine) as session:
        
        create_private_users(session)
        
        for name in names:
            username = generate_username(name)
            email = generate_email(username)
            dept = random.choice(departments)

            user = {
                "name": name,
                "username": username,
                "email": email,
                "password": default_password,
                "dept": dept,
                "currency": "USD"
            }
            
            create_user_and_balance(user, session)

        return {"status": "ok"}
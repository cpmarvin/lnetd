from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from database import Base
from passlib.hash import argon2


class User(Base, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(120), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(30))
    role = Column(String(30), default='user')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value, = value
            if property == 'password':
                setattr(self, property, argon2.hash(value))
            else:
                setattr(self, property, value)

    def get_current_user_role(self):
        return self.role

    def __repr__(self):
        return str(self.username)

    def verify_password(self,password):
        if argon2.verify(password, self.password):
            return True

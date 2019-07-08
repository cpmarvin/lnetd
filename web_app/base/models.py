from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from database import Base
from passlib.hash import argon2

class User(Base, UserMixin):
    
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String(120), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(30))
    role = Column(String(30),default='user')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            print('this is the value',value)
            print('this is the property',property)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value ,= value
            if property == 'password':
                setattr(self,property, argon2.hash(value))
            else:
                setattr(self, property, value)
    def get_current_user_role(self):
        return self.role
        
    def __repr__(self):
        return str(self.username)

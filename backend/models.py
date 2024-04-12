# from tortoise.models import Model
# from tortoise import fields
# from tortoise.contrib.pydantic import pydantic_model_creator

# class User(Model):
#     id                = fields.IntField(pk = True)
#     username          = fields.CharField(max_length=50)
#     password          = fields.CharField(max_length=50)
#     firstname         = fields.CharField(max_length=100)
#     lastname          = fields.CharField(max_length=100)
#     DOB               = fields.CharField(max_length=20)
#     phone_number      = fields.CharField(max_length=50)
#     email             = fields.CharField(max_length=254)
#     address           = fields.CharField(max_length=350)
#     roleID            = fields.IntField (default=0)
    

    
# #Create pydantic models
# user_pydantic   = pydantic_model_creator(User, name="User")
# user_pydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)

from sqlalchemy import Boolean, Column, Integer, String
from database import Base 

class User(Base):
    __tablename__ = 'users'
    
    id                   = Column(Integer, primary_key=True, index= True)
    username             = Column(String(50), unique= True, index= True)
    password             = Column(String(50))
    firstname            = Column(String(50))
    lastname             = Column(String(50))
    DoB                  = Column(String(50))
    address              = Column(String(200))
    email                = Column(String(100))
    phone_number         = Column(String(100))
    roleID               = Column(Integer)
    
class QnA(Base):
    __tablename__ = 'Question and Answer'
    
    id                  = Column(Integer, primary_key=True, index= True)
    title               = Column(String(500))
    content             = Column(String(1000))
    user_id             = Column(Integer)
    
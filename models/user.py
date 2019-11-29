from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
from flask_login import UserMixin, current_user
from flask import request
import os
# from flask_restful import Api, Resource, reqparse
from playhouse.hybrid import hybrid_property


class User(BaseModel, UserMixin):
    username = pw.CharField(unique=True)
    password = pw.CharField()


class Images(BaseModel):
    name = pw.CharField(unique=False)
    image = pw.CharField()
    description = pw.TextField(null=True)
    latitude = pw.TextField()
    longitude = pw.TextField()
    user = pw.ForeignKeyField(User, backref="images")


class Facts(BaseModel):
    images = pw.ForeignKeyField(Images, backref="facts")
    title = pw.CharField(unique=False, null=False)
    text = pw.TextField(null=False)
    user = pw.ForeignKeyField(User, backref="facts")

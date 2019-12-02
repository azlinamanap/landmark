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
    email = pw.CharField(unique=True)
    description = pw.TextField(null=True)
    profilepic = pw.TextField(null=True)

    @hybrid_property
    def profile_image_path(self):
        if self.profilepic:
            return f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/' + self.profilepic
        else:
            return f'https://www.searchpng.com/wp-content/uploads/2019/02/Deafult-Profile-Pitcher.png'

    # PROFILE IMAGE BIG LETTER i


class Images(BaseModel):
    name = pw.CharField(unique=False)
    image = pw.CharField()
    description = pw.TextField(null=True)
    latitude = pw.TextField()
    longitude = pw.TextField()
    user = pw.ForeignKeyField(User, backref="images")
    width = pw.IntegerField()
    height = pw.IntegerField()


class Facts(BaseModel):
    images = pw.ForeignKeyField(Images, backref="facts")
    title = pw.CharField(unique=False)
    text = pw.TextField()
    user = pw.ForeignKeyField(User, backref="facts")

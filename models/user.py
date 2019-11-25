from models.base_model import BaseModel
import peewee as pw
import os
from playhouse.hybrid import hybrid_property


class Landmark(BaseModel):
    name = pw.CharField(unique=False)


class Facts(BaseModel):
    landmark = pw.ForeignKeyField(Landmark, backref="facts")
    title = pw.CharField(unique=False, null=False)
    text = pw.TextField(null=False)


class Images(BaseModel):
    landmark = pw.ForeignKeyField(Landmark, backref="images")
    image = pw.CharField(null=True)

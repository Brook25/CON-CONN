#!/usr/bin/env python3
import mongoengine
from .equipments import Equipment 


class Location(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    city = mongoengine.StringField(required=True)
    sub_city = mongoengine.StringField(required=True)
    equipments = mongoengine.EmbeddedDocumentListField(Equipment)

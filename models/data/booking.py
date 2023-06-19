#!/usr/bin/env python3
import datetime
from mongoengine import EmbeddedDocument, StringField, DateTimeField, EmbeddedDocumentField
from .locations import Location
import mongoengine



class Booking(EmbeddedDocument):
    username = StringField(required=True)
    date = DateTimeField(default=datetime.datetime.utcnow)
    return_date = DateTimeField(required=True)
    location = StringField(required=True)
    item = StringField(required=True)
    name = StringField(required=True)

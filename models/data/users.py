#!/usr/bin/env python3
from flask_login import UserMixin
import mongoengine
from .booking import Booking
from .complaint import Complaint


class User(mongoengine.Document, UserMixin):
    username = mongoengine.StringField(required=True)
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=True)
    material_bookings = mongoengine.EmbeddedDocumentListField(Booking)
    equipment_bookings = mongoengine.EmbeddedDocumentListField(Booking)
    complaints = mongoengine.EmbeddedDocumentListField(Complaint)
    complaints_against = mongoengine.EmbeddedDocumentListField(Complaint)
    notifications = mongoengine.DictField(default={"num": 0, "notes": []})
    
    meta = {"db_alias": "cnn",
            "collection": "users"
            }


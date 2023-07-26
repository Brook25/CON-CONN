#!/usr/bin/env python3
import mongoengine
from mongoengine import StringField
from .booking import Booking
from models.data.locations import ELocation, MLocation

class EquipmentSuppliers(mongoengine.Document):
    """equipment supplier document schema"""
    username = mongoengine.StringField(required=True)
    locations = mongoengine.EmbeddedDocumentListField(ELocation)
    contact_info = mongoengine.ListField(StringField(required=True))
    booked_equipments = mongoengine.EmbeddedDocumentListField(Booking)

    meta = { 'db_alias': 'cnn',
            'collection': 'equipment_suppliers'
            }

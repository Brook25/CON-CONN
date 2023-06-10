#!/usr/bin/env python3
import mongoengine
from mongoengine import StringField
from .booking import Booking
from models.data.locations import Location

class EquipmentSuppliers(mongoengine.Document):
    username = mongoengine.StringField(required=True)
    locations = mongoengine.EmbeddedDocumentListField(Location)
    contact_info = mongoengine.ListField(StringField(required=True))
    booked_equipments = mongoengine.EmbeddedDocumentListField(Booking)

    meta = { 'db_alias': 'cnn',
            'collection': 'equipment_suppliers'
            }

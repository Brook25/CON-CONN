#!/usr/bin/env python3
import mongoengine
from models.data.materials import Material
from models.data.locations import Location
from .booking import Booking


class MaterialSuppliers(mongoengine.Document):
    username = mongoengine.StringField(required=True)
    materials = mongoengine.EmbeddedDocumentListField(Material)
    locations = mongoengine.EmbeddedDocumentListField(Location)
    rating = mongoengine.IntField()
    contact_info = mongoengine.ListField(mongoengine.StringField(required=True))
    booked_materials = mongoengine.EmbeddedDocumentListField(Booking)
    
    meta = { 'db_alias': 'cnn',
            'collection': 'material_suppliers'
            }

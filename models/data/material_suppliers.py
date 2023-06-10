#!/usr/bin/env python3
import mongoengine
from models.data.materials import Material
from models.data.locations import Location
from .booking import Booking


class MaterialSuppliers(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    materials = mongoengine.EmbeddedDocumentListField(Material)
    locations = mongoengine.EmbeddedDocumentListField(Location)
    rating = mongoengine.IntField()
    contact_info = mongoengine.StringField(required=True)
    booked_materials = mongoengine.EmbeddedDocumentListField(Booking)
    
    meta = { 'db_alias': 'my_db',
            'collection': 'material_suppliers'
            }

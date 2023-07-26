#!/usr/bin/env python3
import mongoengine
from models.data.materials import Material
from models.data.locations import MLocation
from .booking import Booking


class MaterialSuppliers(mongoengine.Document):
    """material supplier document schema"""
    username = mongoengine.StringField(required=True)
    locations = mongoengine.EmbeddedDocumentListField(MLocation)
    contact_info = mongoengine.ListField(mongoengine.StringField(required=True))
    booked_materials = mongoengine.EmbeddedDocumentListField(Booking)
    
    meta = { 'db_alias': 'cnn',
            'collection': 'material_suppliers'
            }

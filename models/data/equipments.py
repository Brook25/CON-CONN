import mongoengine
from .materials import Material

class Equipment(Material):
    """equipments document schema"""
    machine = mongoengine.StringField(required=True)
    years_used = mongoengine.IntField()


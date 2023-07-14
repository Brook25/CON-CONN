import mongoengine
from .materials import Material

class Equipment(Material):
    machine = mongoengine.StringField(required=True)
    years_used = mongoengine.IntField()


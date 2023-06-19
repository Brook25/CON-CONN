#!/usr/bin/env python3
import mongoengine
from .equipments import Equipment
from .materials import Material


class Location(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    city = mongoengine.StringField(required=True)
    sub_city = mongoengine.StringField(required=True)
    items = mongoengine.EmbeddedDocumentListField(Material)

    @classmethod
    def append(cls, dct):
        coll = Equipment if dct['coll'][0] == "E" else Material
        items = [coll(**(it)) for it in dct['append']]
        loc = cls(name=dct['filter']['name'], city=dct['filter']['city'], sub_city=dct['filter']['sub_city'],
               items=items)
        dct['username'].locations.append(loc)
        dct['username'].save()


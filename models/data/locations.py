#!/usr/bin/env python3
import mongoengine
from .equipments import Equipment
from .materials import Material


class MLocation(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    city = mongoengine.StringField(required=True)
    sub_city = mongoengine.StringField(required=True)
    items = mongoengine.EmbeddedDocumentListField(Material)
    meta = {'allow_inheritance': True }

    @classmethod
    def append(cls, dct):
        coll = Equipment if dct['coll'][0] == "E" else Material
        items = [coll(**(it)) for it in dct['append']]
        dct['items'] = items
        loc = cls(**dct['filter'])
        dct['user'].locations.append(loc)
        dct['user'].save()
        return items


class ELocation(MLocation):
    items = mongoengine.EmbeddedDocumentListField(Equipment)

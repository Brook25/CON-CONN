import mongoengine

class Material(mongoengine.EmbeddedDocument):
    """materials document schema"""
    name = mongoengine.StringField(required=True)
    available = mongoengine.BooleanField(default=True)
    price = mongoengine.IntField(required=True)
    reviews = mongoengine.ListField(mongoengine.DictField)
    rating = mongoengine.ListField(mongoengine.IntField(), default=[2, 1])
    meta = {'allow_inheritance': True}

    @classmethod
    def append(cls, dct):
        """Embed new material or equipment documents into
           an existing location document.
        """
        materials = [cls(**(it)) for it in dct['append']]
        loc = dct['user'].locations.filter(**(dct['filter'])).first()
        [loc.items.append(mt) for mt in materials]
        dct['user'].save()


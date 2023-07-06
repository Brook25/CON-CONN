import mongoengine
from .materials import Material

class Equipment(Material):
    machine = mongoengine.StringField(required=True)
    years_used = mongoengine.IntField()

    @classmethod
    def append(self, dct):
        equipments = [Equipment(**(eq)) for eq in dct['append']]
        loc = dct['user'].locations.filter(**(dct['filter'])).first()
        print(loc, loc.to_mongo())
        [loc.items.append(eq) for eq in equipments]
        dct['user'].save()

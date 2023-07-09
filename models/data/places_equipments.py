from mongoengine import Document


class PlacesEquipments(Document):

    meta = { 'db_alias': 'cnn',
            'collection': 'places_equipments'
            }

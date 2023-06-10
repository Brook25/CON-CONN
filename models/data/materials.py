import mongoengine

class Material(mongoengine.EmbeddedDocument):
    name = mongoengine.StringField(required=True)
    available = mongoengine.BooleanField(default=True)
    years_used = mongoengine.IntField()
    price = mongoengine.IntField(required=True)
    rating = mongoengine.IntField()

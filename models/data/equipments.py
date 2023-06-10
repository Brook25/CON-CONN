import mongoengine

class Equipment(mongoengine.EmbeddedDocument):
    machine = mongoengine.StringField(required=True)
    name = mongoengine.StringField(required=True)
    available = mongoengine.BooleanField(default=True)
    years_used = mongoengine.IntField()
    price = mongoengine.IntField(required=True)
    reviews = mongoengine.ListField(mongoengine.DictField)
    rating = mongoengine.IntField(default=2)

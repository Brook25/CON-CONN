import mongoengine


class ValidateSupp(mongoengine.Document):
    username = mongoengine.StringField()

    meta = { 'db_alias': 'cnn',
            'collection': 'validate_supp',
            }



class ValidateItem(mongoengine.Document):
    username = mongoengine.StringField()
    location = mongoengine.StringField()
    name = mongoengine.StringField()
    pending = mongoengine.BooleanField()
    item = mongoengine.StringField()
    
    meta = { 'db_alias': 'cnn',
            'collection': 'validate_item'
            }
        
    @classmethod
    def append(cls, dct):
        print(dct)
        loc = '/'.join(dct['filter'].values())
        val_items = [cls(**{'name': x['name'], 'location': loc,
            'username': dct['username'], 'item': dct['item'], 'pending': dct['pending']}) for x in dct['append']]
        #print(dct)
        ValidateItem.objects.insert(val_items)

#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from models.data.equipments import Equipment
from models.data.materials import Material
from models.data.Equipment_suppliers import EquipmentSuppliers
from models.data.material_suppliers import MaterialSuppliers
from models.data.locations import Location
from models.data.booking import Booking
from models.data.users import User
import mongoengine

classes = {'User': User, 'Equipment': Equipment, 'Material': Material, 'MaterialSuppliers': MaterialSuppliers, 'Location': Location, 'EquipmentSuppliers': EquipmentSuppliers, 'Booking': Booking}


class DBEngine:
    __db = None

    def __init__(self):
        #self.__client = MongoClient()
        #self.__db = self.__client['my_db']
        mongoengine.connect(db='my_db', alias='cnn')
        #self.__db = mongoengine.get_db()



    def add_new(self, dct):
       dct['coll'](**dct['docs']).save()

       '''if len(dct.keys()) > 1:
            print(dct)
            coll = self.__db[dct['coll']]
            doc_ids = coll.insert_many(dct['docs'])
            return doc_ids
       raise ValueError("collection name not provided or document name lacking")
       '''
    def find(self, dct):
        coll = classes[dct['coll']]._get_collection()
        all_docs = []
        if len(dct) == 1:
            query = coll.find()
        if 'find' in dct:
            query = coll.find(dct['find'], dct['fields'])
        elif 'agg' in dct:
            query = coll.aggregate(dct['agg'])
        for doc in query:
            all_docs += [doc]
        return all_docs





    def delete(self, dct):
        coll = classes[dct['coll']]._get_collection()
        coll.delete_many(dct['row'])




    def update(self, dct):
        coll = classes[dct['coll']]._get_collection()
        row = dct['row']
        print(coll)
        update = dct['update1']
        if len(dct) < 4:
            coll.update_one(row, update)
        else:
            array_filters = dct['array_filters']
            print(row, update, array_filters)
            coll.update_one(row, update, array_filters=dct['array_filters'], upsert=False)



    def init_validate(self, obj_dict):
        doc = list(obj_dict.keys())[0]
        print(doc)
        for k, v in classes.items():
            if k == doc:
                obj = v(**list(obj_dict.values())[0])
                obj.validate()
                print("OK")
                break




    def feed_history(self, username):
#        pass
        eq_history = self.find({'coll': 'User', 'agg': [{"$match": {"username": username}}, {"$unwind": "$equipment_bookings"}, {"$match": {"equipment_bookings.return_date": {"$gt": datetime.utcnow()} } }, {"$project": {"equipment_bookings": 1, "_id": 0} }] })
        sorted_lst = sorted(eq_history, key=lambda x: x['equipment_bookings']['date'])
        dates = list(map(lambda x: x['equipment_bookings'], eq_history))
        return dates
        #coll = classes['User']._get_collection()
        #coll.insert_one({"history": []})
        #self.update(


        #for doc in eq_history:
        #   print(doc)
        #mt_history = users.find({'coll': 'User', 'agg': [{"$unwind": "material_bookings"}, {"$match": {"material_bookings.date": {"$lt": new Date()} } }, {"$project": {"material_bookings": 1} }] })
        #history = [eq_history + mt_history].sort()
        # inert into history all the values
        #self.update({'coll': 'User', 'row': {"uername": username}, 'update1': {"$pull": {"equipment_bookings": {"equipmemt_bookings.returndate": {"$lt": new Date ()} } } } })
        #self.update({'coll': 'User', 'row': {"uername": username}, 'update1': {"$pull": {"equipment_bookings": {"equipmemt_bookings.returndate": {"$lt": new Date ()} } } } })









#dctj = { 'username': "James", "email": "james1234@gmail.com", "password": "james1234" }

#dctt = { 'username': "Tom", "email": "tom1234@gmail.com", "password": "tommy1234" }

#dctjn = { 'username': "John", "email": "john1234@gmail.com", "password": "john1234" }


#dct1 = {'username': 'Tom', 'locations': [{"name": "Tor-hailoch", "city": "Addis", "sub_city": "Kolfe", 'equipments': [{"machine": "Mixer", "name": "Mixer1", "years_used": 6, "price": 500}, {"machine": "Vibrator", "name": "Vibrator1", "years_used": 4, "price": 1000}, {"machine": "Excavator", "name": "Excavator1", "years_used": 3, "price": 1500}]}]}




#db = DBEngine()


#book_date = datetime.utcnow()
#return_date =  book_date + timedelta(days=3)

#book_date = datetime.utcnow()
#return_date =  book_date + timedelta(days=5)

#print(book_date, return_date)


#db.update({'coll': 'User', 'row': {'username': "John"}, 'update1': {"$push": {"equipment_bookings": { "$each": [{"username": "James", "date": book_date, "name": "Mixer1", "return_date": return_date }, {"username": "Jammie", "date": book_date, "name": "Mixer1", "return_date": return_date} ] } } } })

#val = db.feed_history("John")

#client = MongoClient()
#db = client['my_db']
#db.users.update_one({"history": []}, {"$push": {"history": val}})
#print("done")

#db.delete({'coll': 'User', 'row': {}})
#db.add_new({'coll': User, 'docs': dctt})
#db.add_new({'coll': User, 'docs': dctj})
#db.add_new({'coll': User, 'docs': dctjn})

#print(db.find({'coll': 'User'}))

#db.add_new({'coll': EquipmentSuppliers, 'docs': dct1})
#db.update({'coll': EquipmentSuppliers, 'query': {'username': 'Brook'}, 'update': {'$push': {'locations': {"name": "Kaliti", "sub_city": "Akaki", "city": "Addis", 'equipments': [{"machine": "Mixer", "name": "Mixer1", "years_used": 4, "price": 600}, {"machine": "Compactor", "name": "Compactor1", "years_used": 4, "price": 600}]} } } })
#print(db.find({'coll': 'EquipmentSuppliers'}))




print('done')
#db.find(dct)

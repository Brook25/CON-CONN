#!/usr/bin/env python3

import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from models.data.equipments import Equipment
from models.data.materials import Material
from models.data.Equipment_suppliers import EquipmentSuppliers
from models.data.material_suppliers import MaterialSuppliers
from models.data.locations import MLocation, ELocation
from models.data.users import User
from models.data.booking import Booking
from models.data.validation import ValidateItem, ValidateSupp
from models.data.places_equipments import PlacesEquipments
from mongoengine import connect
import mongoengine

classes = {'User': User, 'Equipment': Equipment, 'Material': Material, 'MaterialSuppliers': MaterialSuppliers, 'MLocation': MLocation, 'ELocation': ELocation, 'EquipmentSuppliers': EquipmentSuppliers, 'PlacesEqs': PlacesEquipments, 'ValSupp': ValidateSupp, 'ValItem': ValidateItem, 'Booking': Booking}


class DBEngine:
    """Database engine that communicates with Mongodb
       to perform queries on collecionts based on Mongoengine classes
    """
    def __init__(self):
        """Initialize engine"""
        mongoengine.connect(db='my_db', alias='cnn')


    def add_new(self, dct):
        """Adds new document to collection based on
           collection name
        """
        classes[dct['coll']](**dct['docs']).save()    


    @staticmethod
    def equipment_count(*args):
        """Counts number of specific equipments registered
           at a location for a supplier inorder to provide proper
           name for newly added equipments.
        """
        it_lst = list(set(map(lambda x: x['machine'], args[0])))
        if len(args) < 2:
            count = [0 for it in it_lst]
        else:
            count = list(map(lambda x: len(args[1].items.filter(machine=x)),
                it_lst))
        count_dct = dict(zip(it_lst, count))
        for it in args[0]:
           it['name'] += str(count_dct[it['machine']] + 1)
           count_dct[it['machine']] += 1

        

    def append_or_create(self, dct):
        """Register or add new materials or equipments for a supplier"""
        coll = classes[dct['coll']]
        supp = coll.objects(username=dct['username']).first()
        if supp:
            dct['user'] = supp
            loc = supp.locations.filter(**(dct['filter'])).first()
            if loc:
                if dct['coll'][0] == "E":
                    self.equipment_count(dct['append'], loc)
                    Equipment.append(dct)
                    dct['item'] = 'equipment'
                else:
                    filter = [loc.items.filter(name=x['name']).first()
                            for x in dct['append']]
                    names = [x['name'] for x in filter if x]
                    dct['append'] = [x for x in dct['append']
                                        if x['name'] not in names]
                    Material.append(dct)
                    dct['item'] = 'material'
                dct['pending'] = True
                if dct['append']:
                    ValidateItem.append(dct)
                return [x['name'] for x in dct['append']]
            else:
                if dct['coll'][0] == "E":
                    self.equipment_count(dct['append'])
                    ELocation.append(dct)
                    dct['item'] = 'equipment'
                else:
                    MLocation.append(dct)
                    dct['item'] = 'material'
                dct['pending'] = True
                ValidateItem.append(dct)
                return [x['name'] for x in dct['append']]
        else:
            if dct['coll'][0] == "E":
                self.equipment_count(dct['append'])
                eq = [Equipment(**(eq)) for eq in dct['append']]
                loc = ELocation(name=dct['filter']['name'],
                        city=dct['filter']['city'],
                        sub_city=dct['filter']['sub_city'], items=eq)
                write_dct = {'username': dct['username'],
                        'locations': [loc], 'contact_info':
                        dct['contact_info']}
                self.add_new({'coll': 'EquipmentSuppliers', 'docs': write_dct})
                dct['item'] = 'equipment'
            else:
                mt = [Material(**(eq)) for eq in dct['append']]
                loc = MLocation(name=dct['filter']['name'],
                        city=dct['filter']['city'],
                        sub_city=dct['filter']['sub_city'], items=mt)
                write_dct = {'username': dct['username'],
                        'locations': [loc], 'contact_info':
                        dct['contact_info'] }
                self.add_new({'coll': 'MaterialSuppliers', 'docs': write_dct})
                dct['item'] = 'material'
            ValidateSupp(username=dct['username']).save()
            dct['pending'] = False
            ValidateItem.append(dct)
            return [x['name'] for x in dct['append']]
            
                


    def find(self, dct):
        """Performs find query"""
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
        """Performs delete query on a specific collection"""
        coll = classes[dct['coll']]._get_collection()
        coll.delete_many(dct['row'])




    def update(self, dct):
        """Performs update query on a collection"""
        coll = classes[dct['coll']]._get_collection()
        row = dct['row']
        update = dct['update1']
        if len(dct) < 4:
            coll.update_one(row, update, upsert=False)
        else:
            array_filters = dct['array_filters']
            coll.update_one(row, update, array_filters=dct['array_filters'],
                    upsert=False)

    
    def places_equipments(self, **kwargs):
        """Creates or Adds new cities, sub_cities or locations and
        Equipment or Material names to the database
        """
        if not (kwargs.get('place') or kwargs.get('materials') or kwargs.get('equipments')):
            raise ValueError('No place, material or equipment key word found')
        my_db = MongoClient("localhost", 27017)['my_db']
        places_equipments = my_db['places_equipments']
        if kwargs.get('place'):
            if not kwargs.get('place').get('cities'):
                raise ValueError('cities not properly provided.')
            places = list(places_equipments.find({'cities': {"$exists": True}}))
            if not places:
                places_equipments.insert_one(kwargs.get('place'))
            else:
                for city in kwargs.get('place').get('cities'):
                    if city not in places['cities']:
                        places_equipments.update({'cities': {"$exists": True}},
                                {"$set": {city: kwargs['place'][city] }})
                    else:
                        for sub_city in kwargs['place']['cities'][city]:
                            places_equipments.update({'cities':
                                {'$exists': True}},
                                {"$addToSet": {f'{city}.{sub_city}':
                                    kwargs['place']['cities'][city][sub_city]}})
                            
        if kwargs.get('materials'):
            places_equipments.update_one({'materials':
                {'$exists': True}}, {"$addToSet": {'materials':
                    {"$each": kwargs.get('materials')} } },
                upsert=True)
        else:
            places_equipments.update_one({'equipments': {'$exists': True}},
                    {"$addToSet": {'equipments': {"$each":
                        kwargs.get('equipments')} } },
                    upsert=True)




    def feed_history(self, username):
        """Move bookings whose return date is due into history
           while loading home page, and notify user.
        """
        eq_history = self.find({'coll': 'User',
            'agg': [{"$match": {"username": username}},
            {"$unwind": "$equipment_bookings"},
            {"$match": {"equipment_bookings.return_date":
            {"$lt": datetime.utcnow()} } },
            {"$project": {"equipment_bookings": 1, "_id": 0} }] 
            })
        eq_lst = []
        for dct in eq_history:
            if {'username': dct['equipment_bookings']['username'],
                'location': dct['equipment_bookings']['location']} 
                not in eq_lst:
                eq_lst += [{'username': dct['equipment_bookings']['username'],
                    'location': dct['equipment_bookings']['location']}]
        for item in eq_lst:
            item['name'] = []
            for eq in eq_history:
                if item['username'] == eq['equipment_bookings']['username']
                and item['location'] == eq['equipment_bookings']['location']:
                item['name'] += [eq['equipment_bookings']['name']]
        for eq in eq_lst:
            loc = eq['location'].split('/')
            self.update({'coll': 'EquipmentSuppliers',
            'row': {'username': eq['username']},
            'update1':{"$set": {"locations.$[l].items.$[i].available": True}},
            'array_filters': [{'l.name': loc[0],
                'l.sub_city': loc[1], 'l.city': loc[2]},
            {'i.name': {'$in': eq['name']}}]})
        mt_history = self.find({'coll': 'User',
            'agg': [{"$match": {"username": username}},
                {"$unwind": "$material_bookings"},
                {"$match": {"material_bookings.return_date":
                    {"$lt": datetime.utcnow()} } },
                {"$project": {"material_bookings": 1, "_id": 0} }] })
        self.update({'coll': 'User',
            'row': {"username": username},
            'update1': {"$pull":  {"equipment_bookings":
                {"return_date": {"$lt": datetime.utcnow()} },
                "material_bookings": {"return_date":
                    {"$lt": datetime.utcnow()} } } }
                })
        self.update({'coll': 'EquipmentSuppliers',
            'row': {"username": username},
            'update1': {"$pull": {"booked_equipments":
                {"return_date": {"$lt": datetime.utcnow() } } } }
            })
        self.update({'coll': 'MaterialSuppliers',
            'row': {"username": username},
            'update1': {"$pull": {"booked_materials":
                {"return_date": {"$lt": datetime.utcnow() } } } }
            })
        history = list(map(lambda x: x['equipment_bookings'], eq_history))
        + list(map(lambda x: x['material_bookings'], mt_history))
        history = sorted(history, key=lambda x: x['date'])
        self.update({'coll': 'User', 'row': {'username': username},
            'update1': {'$push': {"history": {"$each": history} } }
            })

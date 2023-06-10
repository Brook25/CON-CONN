#!/usr/bin/env python3
from users import User
from equipments import Equipment
from materials import Material
from material_suppliers import MaterialSuppliers
from Equipment_suppliers import EquipmentSuppliers
from locations import Location
from models import engine
from booking import Booking
import json
#from mongoengine import connect
#import pymongo


#connect(db="my_db", alias="cnn")


def try_one():
    User(username="James", email="jamesbond@gmail.com", password="james1234").save()
    #User(username="John", email="johnblake@gmail.com", password="john1234").save()
    #eq1 = Equipment(machine="Mixer", name="Mixer1", years_used=5, price=400)
    #eq2 = Equipment(machine="Mixer", name="Mixer2", years_used=3, price=300)
    #loc = {"name": "Tor-hailoch", "city": "Addis", "sub_city": "Kolfe", "equipments": [eq1, eq2]}
    #EquipmentSuppliers(username="James", contact_info = ["0911234567","0923456789"], locations=[loc]).save()
    print("done")

query = engine.find({'coll': 'equipment_suppliers', 'row': {'locations.name': "Tor-hailoch", "locations.city": "Addis", "locations.sub_city": "Kolfe", "locations.equipments.machine": {"$in": ["Mixer"] } } })

print(query)

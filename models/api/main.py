#!/usr/bin/env python3


from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse, abort
from models.engine import engine
import json

app = Flask(__name__)
CORS(app, support_credentials=True)
api = Api(app)




class Locations(Resource):

    def get(self, item_type):
        if item_type == "all":
            print(request.args)
            e = engine.find({'coll': 'EquipmentSuppliers', 'find': {"username": request.args.get('uname') }, 'fields': {'locations': 1, '_id': 0} })[0]['locations']
            e = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in e]
            m = engine.find({'coll': 'MaterialSuppliers', 'find': {"username": request.args.get('uname')}, 'fields': {'locations': 1, '_id': 0} })[0]['locations']
            m = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in m]
            return jsonify({"e": e, "m": m})
    
    def post(self, item_type):
        if item_type == "all":
            pass

class Items(Resource):

    def get(self, item_type):
        print(request.args)
        if 'locations' in request.args:
            uname = request.args.get('user')
            location = request.args.get('locations').split('/')
            name = location[0]
            city = location[1]
            sub_city = location[2]
            coll = 'EquipmentSuppliers' if item_type == 'equipment' else 'MaterialSuppliers'
            query = engine.find({"coll": coll, "find": {"username": uname, "locations.name": name,
                "locations.sub_city": sub_city, "locations.city": city}, "fields": {"locations.items": 1, "_id": 0} })[0]['locations'][0]['items']
            return json.dumps(query)
    def post(self, item_type):
        post_args = reqparse.RequestParser()
        post_args.add_argument("location", type="str", help="Location is required", required=True)
        post_args.add_argument("items", type="str", help="A list of materials is required", required=True)
        post_args = post_args.parse_args()
        return None
        
    def delete(self, item_type):
        if locations in request.args and locations:
            for item in items:
                pass
        return None

    @staticmethod
    def abort_if_not_item_type(item_type):
        if item_type not in ['Equipments', 'Materials']:
            abort("Item type not found")
        return None
        

class Complaints(Resource):
    def get(self):
        if 'user_id' in request.args:
            pass
        return None
    def post(self):
        post_args = reqparse.RequestParser()
        post_args.add_argument("user_id", type="str", help="Location is required", required=True)
        post_args.add_argument("complaint", type="str", help="A list of materials is required", required=True)
        post_args.add_argument("by", type="str", help="id of the complainer is needed")
        post_args = post_args.parse_args()
        return None

    def delete(self):
        if locations in request.args and locations:
            for item in items:
                pass
        return None

    @staticmethod
    def abort_if_not_item_type(item_type):
        if item_type not in ['Equipments', 'Materials']:
            abort("Item type not found")

        return None



class Reviews(Resource):
    def get(self, item_or_task):
        if 'user_id' in request.args and 'location' in request.args\
                and 'name' in request.args:
            pass
        return None
    
    def post(self, item_or_task):
        print(item_or_task)
        if item_or_task == "equipments":
            print(request.json['uname'])
            return json.dumps([{"name": "John", "review": "it was great. But the motor value of the thing should be working on the other side"},
                                {"name": "James", "review": "it was great. But the techincal value of the thing should be working on the other side"}
                                ])
        elif item_or_task == "materials":
            pass
        
        else:
            print(item_or_task)
            req = json.loads(request.get_json())
            print(type(req), req)
            current_user = req.get('uname')
            supp = req.get('supp').split(':')
            supp_name = supp[0]
            print(supp)
            loc = supp[1].split('-')
            print(loc)
            name = supp[2]
            item = supp[-1]
            rev = {"username": current_user, "review": req.get("rev")}
            coll = 'EquipmentSuppliers' if item[0] == 'e' else 'MaterialSuppliers'
            engine.update({'coll': coll, 'row': {'username': supp_name}, 'update1': {"$push": {"locations.$[ln].items.$[it].reviews": rev}}, "array_filters": [{"ln.name": loc[0]+'-'+loc[1], "ln.sub_city": loc[2], "ln.city": loc[3]}, {"it.name": name}]})
            print("done")
            return None, 200

        
        

    def delete(self, item_or_task):
        if locations in request.args and locations:
            for item in items:
                pass
        return None

    @staticmethod
    def abort_if_not_item_type(item_type):
        if item_type not in ['Equipments', 'Materials']:
            abort("Item type not found")

        return None


class History(Resource):
    def get(self, user):
        print(user)
        history = engine.find({'coll': 'User', 'find': {"username": user}, 'fields': {"history": 1, "_id": 0} })[0]['history']
        for h in history:
            h['date'] = h['date'].isoformat()
            h['return_date'] = h['return_date'].isoformat()
        return json.dumps(history)


class Notification(Resource):
    def get(self, notn):
        print(notn)
        if notn > 0:
            pass
            #change the notification no value to 0
        #find the messages in notification and return them
        return json.dumps(["you have a review", "you have a comment"])


class Change(Resource):
    def post(self, option):
        uname = request.form.get('uname')
        detail = request.form.get('detail').split(':')
        location = detail[1].split('/')
        change = request.form.get('change').split(':')
        print(detail)
        coll = 'EquipmentSuppliers' if detail[0] == 'eq' else 'MaterialSuppliers'
        if option == "price":
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$set": {"locations.$[l].equipments.$[e].price": change[1]}}, "array_filters": [{"l.name": name, "l.sub_city": sub_city, "l.city": city}, {"e.name": name}] })
        
        elif option == "location":
            query = engine.find({'coll': coll, 'agg': [{"$match": {"username": "John"}}, {"$unwind": "$locations"}, {"$match": {"locations.name": "Tor-hailoch", "locations.sub_city": "Kolfe", "locations.city": "Addis"}}, {"$unwind": "$locations.equipments"}, {"$match": {"locations.equipments.name": "Mixer1"}}, {"$project": {"locations.equipments": 1, "_id": 0}}]})[0]['locations']['equipments']
            engine.update({'coll': coll, 'row': {"username": uname},
            'update1': {"$pull": {"locations.$[l].equipments": {"name": "Excavator1"}}}, 'array_filters': [{"l.name": "Tor-hailoch", "l.sub_city": "Kolfe", "l.city": "Addis"}] })
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$push": {"locations.$[l].equipments": query}}, 'array_filters': [{"l.name": "Tor-hailoch", "l.sub_city": "Kolfe", "l.city": "Addis"}] })
        
        else:
            for c in change:
                engine.find_and_update({'coll': coll, 'row': {"username": uname}, 'update': [{"$set": {"locations.$[l].equipments.$[e].avialabile":{"$eq": [False, "$present"]} }}], "array_filters": [{"l.name": name, "l.sub_city": sub_city, "l.city": city}, {"e.name": c}]})
        
        return json.dumps({'res': 'ok'})



api.add_resource(Locations, '/locations/<string:item_type>')
api.add_resource(Items, '/item/<string:item_type>')
api.add_resource(Complaints, '/complaints/<string:item_type>/<string:supp_id>')
api.add_resource(Reviews, '/reviews/<string:item_or_task>')
api.add_resource(History, '/history/<string:user>')
api.add_resource(Notification, '/notification/<int:notn>')
api.add_resource(Change, '/change/<string:option>')

if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')

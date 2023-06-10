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
            return jsonify({"e": ["Addis/Kolfe/Tor-hailoch", "addis/kolfe/total"], "m": ["addis/kolfe/tor-hailoch", "addis/kolfe/total"]})
    
    def post(self, item_type):
        if item_type == "all":
            pass

class Items(Resource):

    def get(self, item_type):
        print(request.args)
        if 'locations' in request.args:
            uname = request.args.get('user')
            print(uname)
            location = request.args.get('locations').split('/')
            city = location[0]
            sub_city = location[1]
            name = location[2]
            query = engine.find({"coll": 'EquipmentSuppliers', "find": {"username": uname, "locations.name": name,
                "locations.sub_city": sub_city, "locations.city": city}, "fields": {"locations.equipments": 1, "_id": 0} })
            #print(query)
            #return json.dumps({"1": 1})
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
        #post_args = reqparse.RequestParser()
        #post_args.add_argument("uname", type="str", help="user_id is required", required=True)
        #post_args.add_argument("loc", type="str", help="name of location is required", required=True)
        #post_args.add_argument("name", type="str", help="name of item is required", required=True)
        #post_args = post_args.parse_args()
        if item_or_task == "equipments":
            print(request.json['uname'])
            return json.dumps([{"name": "John", "review": "it was great. But the motor value of the thing should be working on the other side"},
                                {"name": "James", "review": "it was great. But the techincal value of the thing should be working on the other side"}
                                ])
        elif item_or_task == "materials":
            pass
        
        else:
            req = request.get_json()
            print(type(req), req)
            current_user = req.get('uname')
            supp = req.get('supp').split(':')
            supp_name = supp[0]
            loc = supp[1].split('/')
            print(loc)
            item = supp[2]
            name = supp[3]
            rev = {"username": current_user, "review": req.get("rev")}
            if item != '-':
                engine.update({'coll': 'EquipmentSuppliers', 'row': {'username': supp_name}, 'update1': {"$push": {"locations.$[ln].equipments.$[eq].reviews": rev}}, "array_filters": [{"ln.name": loc[0], "ln.sub_city": loc[1], "ln.city": loc[2]}, {"eq.name": "Mixer1"}]})
                print("done")
            return None, 200

        
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


class History(Resource):
    def get(self):
        if request.args.get('user'):
            uname = request.args.get('user')
            print(uname)
            #history = db.engine.find({'row': {"username": uname}, 'find': {"history": 1, "_id": 0} })
            return json.dumps([{"username": "James", "location": "tot/kolfe/rdr/", "name": "Mixer1"}, {"username": "pete", "location": "mex/lafto/rdr/", "name": "Mixer1"}])
            #return json.dumps(history)




api.add_resource(Locations, '/locations/<string:item_type>')
api.add_resource(Items, '/item/<string:item_type>')
api.add_resource(Complaints, '/complaints/<string:item_type>/<string:supp_id>')
api.add_resource(Reviews, '/reviews/<string:item_or_task>')
api.add_resource(History, '/history')


if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')

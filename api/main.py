#!/usr/bin/env python3
"""Api endpoint classes"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse, abort
from engine import engine
import json
import math

app = Flask(__name__)
CORS(app, support_credentials=True)
api = Api(app)




class Locations(Resource):
    """location endpoint. Based on item_type
       returns available locations fori
       equipments, materials or both.
    """

    def get(self, item_type):
        """resonds to get requests to the api,
        returns available locations.
        """
        if item_type == "all":
            print(request.args)
            e = engine.find({'coll': 'EquipmentSuppliers', 'find': {"username": request.args.get('uname') }, 'fields': {} })
            if e:
                e = e[0]['locations']
            e = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in e]
            m = engine.find({'coll': 'MaterialSuppliers', 'find': {"username": request.args.get('uname')}, 'fields': {} })
            if m:
                m = m[0]['locations']
            m = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in m]
            return jsonify({"e": e, "m": m})
    

class Items(Resource):
    """Perform queries on registered materials
       or equipments based on a given location
    """

    def get(self, item_type):
        """Get registered equipments or matrials
           from a given location based on supplier username.
        """
        if 'locations' in request.args:
            uname = request.args.get('user')
            location = request.args.get('locations').split('/')
            name = location[0]
            city = location[1]
            sub_city = location[2]
            coll = 'EquipmentSuppliers' if item_type == 'equipment' else 'MaterialSuppliers'
            query = engine.find({"coll": coll, "find": {"username": uname}, "fields": {} })[0]['locations']
            res = [loc for loc in query if loc['name'] == name and loc['city'] == city and loc['sub_city'] == sub_city][0]['items']
            return json.dumps(res)
        
    def delete(self, item_type):
        """Delete an equipment or a material of
        a suppier based on a given location.
        """
        data = json.loads(request.json)
        detail = data.get('detail').split('/')
        name, city, sub_city = detail[0], detail[1], detail[2]
        print(data, detail, name, city)
        coll = 'EquipmentSuppliers' if item_type == "equipment" else 'MaterialSuppliers'
        engine.update({'coll': coll, 'row': {"username": data['uname']},
            'update1': {"$pull": {"locations.$[l].items": {"name": {"$in": data['change'] } } } },
            'array_filters': [{"l.name": name, "l.city": city, "l.sub_city": sub_city}] })
        engine.update({'coll': 'User', 'row': {'username': data['uname']}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully removed {' '.join(data['change'])} at {name}/{sub_city}/{city}"], "$position": 0 } } } })
        return json.dumps({"res": 'OK'})

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
    """Perform queries on  reviews of materials
       or equipments based on a given location
    """
    def post(self, item_or_task):
        """Adds or returns reviews for a particular material or equipment"""
        if item_or_task != "add_review":
            coll = 'MaterialSuppliers' if item_or_task == 'materials' else 'EquipmentSuppliers'
            req = request.json
            loc = req.get('loc').split('/')
            name = req.get('name')[:-2]
            reviews = engine.find({'coll': coll, 'agg': [{'$match': {'username': req.get('uname') }}, {"$unwind": "$locations"}, {"$match": {"locations.name": loc[0], "locations.sub_city": loc[1], "locations.city": loc[2] } }, {"$unwind": "$locations.items"}, {"$match": {"locations.items.name": name}}, {"$project": {'locations.items.reviews': 1, '_id': 0}} ] })[0]['locations']['items'].get('reviews')
            return json.dumps(reviews)
        
        else:
            req = json.loads(request.get_json())
            current_user = req.get('uname')
            supp = req.get('supp').split(':')
            supp_name = supp[0]
            loc = supp[1].split('/')
            name = supp[2]
            rev = {"username": current_user, "review": req.get("rev")}
            rat = int(req.get('rating'))
            coll = 'EquipmentSuppliers' if supp[-1][0] == 'e' else 'MaterialSuppliers'
            rev_rat = engine.find({'coll': coll, 'agg': [{'$match': {'username': supp_name }}, {"$unwind": "$locations"}, {"$match": {"locations.name": loc[0], "locations.sub_city": loc[1], "locations.city": loc[2] } }, {"$unwind": "$locations.items"}, {"$match": {"locations.items.name": name}}, {"$project": {'locations.items.rating': 1, 'locations.items.reviews': 1, '_id': 0}} ] })[0]['locations']['items']
            reviews = rev_rat['reviews']
            rating = rev_rat['rating']
            exists = False
            for rev in reviews:
                if rev['username'] == current_user:
                    exists = True
                    break
            if not exists:
                rating[0] = round(rating[0], 2)
                new_rat = [(rating[0] + rat) / (rating[1] + 1), rating[1] + 1]
                engine.update({'coll': coll, 'row': {'username': supp_name}, 'update1': {"$push": {"locations.$[l].items.$[i].reviews": rev}, "$set": {"locations.$[l].items.$[i].rating": new_rat}}, 'array_filters': [{"l.name": loc[0], "l.city": loc[2], "l.sub_city": loc[1]}, {"i.name": name}] })
                return 'ok', 200
            return 'Not Done', 200

        
class History(Resource):
    """Fetches history of a user's activites"""
    def get(self, user):
        history = engine.find({'coll': 'User', 'find': {"username": user}, 'fields': {"history": 1, "_id": 0} })[0]['history']
        for h in history:
            h['date'] = h['date'].isoformat()
            h['return_date'] = h['return_date'].isoformat()
        print(history)
        return json.dumps(history)


class Notification(Resource):
    """Adds and fetches notifications for a user"""
    def get(self, notn):
        uname = request.args.get('uname')
        if notn > 0:
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': {'$set': {'notifications.num': 0} } } )
        nots = engine.find({'coll': 'User', 'agg': [{'$match': {'username': uname} }, {"$project": {"_id": 0, "notifications.notes": {"$slice": ["$notifications.notes", 25] } }}] })[0]['notifications']['notes']

        return json.dumps(nots)


class Change(Resource):
    """Performs updates and changes on specific
       material and equipment data
    """
    def post(self, option, item):
        uname = request.form.get('uname')
        loc = request.form.get('detail').split('/')
        change = request.form.get('change').split(':')
        new_loc = change[1].split('/')
        coll = 'EquipmentSuppliers' if item == 'equipment' else 'MaterialSuppliers'
        if option == "Price":
            print('hello', loc, change, new_loc,request.form)
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$set": {"locations.$[l].items.$[i].price": int(change[1])}}, "array_filters": [{"l.name": loc[0], "l.sub_city": loc[2], "l.city": loc[1]}, {"i.name": change[0]}] })
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully changed the price of a {item} {change[0]} at {loc[0]}/{loc[2]}/{loc[1]}"], "$position": 0 } } } })
        
        elif option == "location":
            pull, count = None, 0
            if sorted(new_loc) != sorted(loc):
                query = engine.find({'coll': coll, 'find': {'username': uname}, 'fields': {} })[0]['locations']
                for l in query:
                    if l['city'] == loc[1] and l['sub_city'] == loc[2] and l['name'] == loc[0]:
                        for it in l['items']:
                            if it['name'] == change[0]:
                                pull = it
                                break
                    elif item == "equipment" and l['city'] == new_loc[0] and l['sub_city'] == new_loc[1] and l['name'] == new_loc[2]:
                        for it in l['items']:
                            if it['machine'] in change[0]:
                                count += 1
                        if pull:
                            if item == "material":
                                break
                            elif item != "material" and count:
                                break
                if item == "equipment":
                    pull['name'] = f'{pull["machine"]}{count + 1}'

            
                engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$push": {"locations.$[l].items": pull}}, 'array_filters': [{"l.name": new_loc[2], "l.sub_city": new_loc[1], "l.city": new_loc[0]}] })
            
                engine.update({'coll': coll, 'row': {"username": uname},
            'update1': {"$pull": {"locations.$[l].items": {"name": change[0]}}}, 'array_filters': [{"l.name": loc[0], "l.sub_city": loc[2], "l.city": loc[1]}] })
                engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully changed the location of a {item} {change[0]} from {loc[0]}/{loc[2]}/{loc[1]} to {new_loc[2]}/{new_loc[1]}/{new_loc[0]}"], "$position": 0 } } } })
        else:
            change.pop()
            query = engine.find({'coll': coll, 'agg': [{"$match": {"username": uname} } , {"$unwind": "$locations"}, {"$match": {"locations.name": loc[0], "locations.city": loc[1], "locations.sub_city": loc[2]}}, {"$project": {"locations.items": {"$filter": {"input": "$locations.items", "as": "inner_doc", "cond": {"$in": ["$$inner_doc.name", change] } } } } } ] })[0]['locations']['items']
            av = dict([[item['name'].lower(), not(item['available'])] for item in query])
            it_names = sorted([item['name'] for item in query])
            update1 = {f"locations.$[l].items.$[{k.replace('-', '').replace(' ', '')}].available":  av[k] for k in sorted(av.keys())}
            array_filters = [{"l.name": loc[0], "l.sub_city": loc[2], "l.city": loc[1]}]+ [{f"{k.lower().replace('-', '').replace(' ', '')}.name": k} for k in it_names]
            dct = {'coll': coll, 'row': {"username": uname}, 'update1': {"$set": update1}, 'array_filters': array_filters}
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$set": update1}, 'array_filters': array_filters})
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully changed the visibility of a {item} {change[0]} at {loc[0]}/{loc[2]}/{loc[1]}"], "$position": 0 } } } })
            

         
        return json.dumps({'res': 'ok'})



api.add_resource(Locations, '/locations/<string:item_type>')
api.add_resource(Items, '/item/<string:item_type>')
api.add_resource(Complaints, '/complaints/<string:item_type>/<string:supp_id>')
api.add_resource(Reviews, '/reviews/<string:item_or_task>')
api.add_resource(History, '/history/<string:user>')
api.add_resource(Notification, '/notification/<int:notn>')
api.add_resource(Change, '/change/<string:option>/<string:item>')






if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')

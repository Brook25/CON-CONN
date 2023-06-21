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
            e = engine.find({'coll': 'EquipmentSuppliers', 'find': {"username": request.args.get('uname') }, 'fields': {} })
            if e:
                e = e[0]['locations']
            e = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in e]
            m = engine.find({'coll': 'MaterialSuppliers', 'find': {"username": request.args.get('uname')}, 'fields': {} })
            if m:
                m = m[0]['locations']
            m = [f'{x["name"]}/{x["city"]}/{x["sub_city"]}' for x in m]
            return jsonify({"e": e, "m": m})
    
    def post(self, item_type):
        if item_type == "all":
            pass

class Items(Resource):

    def get(self, item_type):
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
    def post(self, item_type):
        post_args = reqparse.RequestParser()
        post_args.add_argument("location", type="str", help="Location is required", required=True)
        post_args.add_argument("items", type="str", help="A list of materials is required", required=True)
        post_args = post_args.parse_args()
        return None
        
    def delete(self, item_type):
        data = json.loads(request.json)
        detail = data.get('detail').split('/')
        name, city, sub_city = detail[0], detail[1], detail[2]
        print(data, detail, name, city)
        coll = 'EquipmentSuppliers' if item_type == "equipment" else 'MaterialSuppliers'
        engine.update({'coll': coll, 'row': {"username": data['uname']},
            'update1': {"$pull": {"locations.$[l].items": {"name": {"$in": data['change'] } } } },
            'array_filters': [{"l.name": name, "l.city": city, "l.sub_city": sub_city}] })
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
    def post(self, option, item):
        uname = request.form.get('uname')
        loc = request.form.get('detail').split('/')
        change = request.form.get('change').split(':')
        new_loc = change[1].split('/')
        coll = 'EquipmentSuppliers' if item == 'equipment' else 'MaterialSuppliers'
        print(change, new_loc, loc)
        if option == "Price":
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$set": {"locations.$[l].items.$[i].price": int(change[1])}}, "array_filters": [{"l.name": loc[0], "l.sub_city": loc[2], "l.city": loc[1]}, {"i.name": change[0]}] })
        
        elif option == "location":
            pull, count = None, 0
            query = engine.find({'coll': coll, 'find': {'username': uname}, 'fields': {} })[0]['locations']
            for l in query:
                if l['city'] == loc[1] and l['sub_city'] == loc[2] and l['name'] == loc[0]:
                    print(l)
                    for it in l['items']:
                        if it['name'] == change[0]:
                            pull = it
                            break
                elif item == "equipment" and l['city'] == new_loc[0] and l['sub_city'] == new_loc[1] and l['name'] == new_loc[2]:
                    print(l)
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
            return json.dumps({"res": "ok"})


        else:
            change.pop()
            query = engine.find({'coll': coll, 'agg': [{"$match": {"username": uname} } , {"$unwind": "$locations"}, {"$match": {"locations.name": loc[0], "locations.city": loc[1], "locations.sub_city": loc[2]}}, {"$project": {"locations.items": {"$filter": {"input": "$locations.items", "as": "inner_doc", "cond": {"$in": ["$$inner_doc.name", change] } } } } } ] })[0]['locations']['items']
            av = dict([[item['name'].lower(), not(item['available'])] for item in query])
            update1 = {f"locations.$[l].items.$[{k}].available":  av[k] for k in sorted(av.keys())}
            array_filters = [{"l.name": loc[0], "l.sub_city": loc[2], "l.city": loc[1]}]+ [{f"{k}.name": k[0].upper() + k[1:]} for k in sorted(av.keys())]
            dct = {'coll': coll, 'row': {"username": uname}, 'update1': {"$set": update1}, 'array_filters': array_filters}
            print(dct)
            engine.update({'coll': coll, 'row': {"username": uname}, 'update1': {"$set": update1}, 'array_filters': array_filters})
            

         
            return json.dumps({'res': 'ok'})



api.add_resource(Locations, '/locations/<string:item_type>')
api.add_resource(Items, '/item/<string:item_type>')
api.add_resource(Complaints, '/complaints/<string:item_type>/<string:supp_id>')
api.add_resource(Reviews, '/reviews/<string:item_or_task>')
api.add_resource(History, '/history/<string:user>')
api.add_resource(Notification, '/notification/<int:notn>')
api.add_resource(Change, '/change/<string:option>/<string:item>')



#query = engine.find({'coll': coll, 'agg': [{"$match": {"username": uname}}, {"$unwind": "$locations"}, {"$match": {"locations.name": location[0], "locations.sub_city": location[2], "locations.city": location[1]}}, {"$unwind": "$locations.items"}, {"$match": {"locations.items.name": change[0]}}, {"$project": {"locations.items": 1, "_id": 0}}]})[0]['locations']['items']




if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')

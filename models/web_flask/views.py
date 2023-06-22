#!/usr/bin/env python3
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from models.engine import engine
from models.data.users import User
import json
import requests




views = Blueprint('views', __name__)
cities = {'Addis': {'subcities': {'Kolfe': {'locations': ['tor-hailoch', 'ayer-tena']}, 'lafto': { 'locations': ['weyra', 'akaki']}, 'kaliit': { 'locations': ['total', 'mexico', 'golf-club']}}}, 'Hawassa': {'subcities': {'Atote': {'locations': ['tor-hailoch', 'ayer-tena']}, 'Harar-sefer': { 'locations': ['weyra', 'akaki']}, 'Piassa': { 'locations': ['total', 'mexico', 'golf-club']}}}}



@views.route('/')
@login_required
def home():
    return render_template("home.html")



@views.route('/query/<string:item>', methods=["POST", "GET"])
def query(item):
    query = json.loads(request.args.get('query1'))
    #print(query[0]['locations']['items'])
    loc = request.args.get('loc').split('/')
    loc = {"name": loc[1], "sub_city": loc[2], "city": loc[3]}
    if request.method == "POST":
        bookings = request.form.get('supp')
        if bookings:
            bookings = bookings[:-2].split(', ')
        uname = current_user.username
        coll = 'EquipmentSuppliers' if item == "equipment" else 'MaterialSuppliers'
        for book in bookings:
            details = book.split('-')

            print(book, details, bookings, loc, item)
            engine.update({'coll': coll, 'row': {'username': details[0]}, 'update1': {"$set": { "locations.$[ln].items.$[it].available": False } }, "array_filters": [ {"ln.name": loc['name'], "ln.city": loc['city'], "ln.sub_city": loc['sub_city'] }, {"it.name": details[1]} ] })
            engine.update({'coll': 'User', 'row': {'username': details[0]}, 'update1': { "$inc": { "notifications.num": 1 }, "$set": {"notifications.not": f"One of your {item}s has been booked"} } })
            
            days = 1 if item == 'material' else int(request.args.get('days'))
            booking = {"username": details[0], "location": ('/').join(loc.values()), 'item': item , "name": details[1], 'date': datetime.utcnow()}
            booking['return_date'] = booking['date'] + timedelta(days=days)
            booked = booking.copy()
            booked["username"] = uname
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': {"$push":  {f"{item}_bookings": booking } } } )
            engine.update({'coll': coll, 'row': {'username': details[0]}, 'update1': {"$push":  {f"booked_{item}s": booked } } })
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$set": {"notifications.not": f"You have successfully booked a {item}" } } })
        flash(f"Equipment succesfully booked", "success")
        return "<h1>Done!<\h1>"
        #return redirect(url_for("views.welcome"))
    print(query)
    return render_template("queries.html", query=query)



@views.route('/user-login', methods=["POST", "GET"])
@login_required
def welcome():
    locations = ["Total", "Mexico", "Piassa"]
    #nots = engine.find({'coll': 'User', 'find': {'username': current_user.username}, 'fields': {"notifications": 1, "_id": 0} } )
    nots = 3
    if request.method == "POST":
        city = request.form.get('city')
        sub_city = request.form.get('sub-city')
        location = request.form.get('location')
        equipment = request.form.get('equipment') 
        return redirect(url_for('views.query', query=query))
        

        #print(city, sub_city, location, equipment)
    engine.feed_history(current_user.username)
    return render_template("welcome.html", cities=cities, equipments=equipments, nots=nots, uname=current_user.username)

@views.route('/city', methods=["POST", "GET"])
def city():
    global cities
    if request.method == "POST":
       city_name = request.form['place']
       print(city_name)
       res = list(cities[city_name]['subcities'].keys())
       return jsonify(res)

    
@views.route('/sub-city', methods=["POST", "GET"])
def sub_city():
    global cities
    if request.method == "POST":
       name = request.form['place'].split('/')
       print("hey, there", name)
       city_name = name[0]
       subc_name = name[1]
       print(subc_name)
       res = cities[city_name]['subcities'][subc_name]['locations']
       print(res)
       return jsonify(res)

@views.route('/location', methods=["POST", "GET"])
def equipments():
    if request.method == "POST":
        return jsonify(equipments)




@views.route('/book/<string:item>', methods=["POST", "GET"])
@login_required
def book(item):
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]
    materials = ["Sand", "Steel", "Aggregate", "Cement"]

    if request.method == "POST":
        if item == 'equipment':
            coll = 'EquipmentSuppliers'
            selector = "machine"
        else:
            coll = 'MaterialSuppliers'
            selector = "name"
        city = request.form.get('city')
        sub_city = request.form.get('sub-city').split('/')[1]
        location = request.form.get('location')
        equipments = request.form.get('equipment').split(', ')
        query1 = engine.find({'coll': coll, 'agg': [{"$unwind": "$locations"}, {"$unwind": "$locations.items"}, {"$match": {"locations.name": location, "locations.city": city, "locations.sub_city": sub_city, f"locations.items.{selector}": { "$in": equipments } } }, {"$project": {"_id": 0, "username": 1, "locations.items": 1, "contact_info": 1} }] })
        print(city, sub_city, location, equipments)
        loc = f"{item}/{location}/{sub_city}/{city}"
        return redirect(url_for('views.query', item=item, query1=json.dumps(query1), loc=loc, days=request.form.get('days')))
    if item == 'equipment':
        items = ('Equipment(s)', equipments)
    else:
        items = ('Material(s)', materials)
    return render_template('book.html', cities=cities, items=items)



@views.route('/register/<string:type>/<string:item>', methods=["POST", "GET"])
@login_required
def register(type, item):
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]
    materials = ["Sand", "Steel", "Aggregate", "Cement"]
    if request.method == "POST":
        coll = 'EquipmentSuppliers' if item == 'equipment' else 'MaterialSuppliers'
        form = request.form
        city = form.get('city')
        sub_city = form.get('sub-city').split('/')[1]
        location = form.get('location')
        it_lst = [x for x in ['it1', 'it2', 'it3'] if form.get(x)]
        values = []
        for it in it_lst:
            val = {'price': form.get(f'{it}-price'), 'name': form.get(it)}
            if item == "equipment":
                val['years_used'] = form.get(f'{it}-yused')
                val['machine'] = form.get(it)
            values += [val]
        uname = current_user.username        
        dct = {"coll": coll, 'username': uname, 'filter':
                {'name': location, 'sub_city': sub_city,
                'city': city}, 'append': values}
        print(dct)
        if type == 'new':
            dct['contact_info'] = form.get('contactinfo')
        engine.append_or_create(dct)
        return "<h1>Done</h1>"
        #return redirect(url_for('views.query', query1=json.dumps(query1), loc=loc))
    if item == 'equipment':
        items = ('Equipment', equipments)
        #print(request.args.get('item'))
    else:
        items = ('Material', materials)
    #print(items[0][0])
    return render_template('become_supp.html', cities=cities, items=items)







@views.route('/supply', methods=["POST", "GET"])
@login_required
def supply():
    global cities
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]

    return render_template('supply.html', cities=cities, equipments=equipments)


@views.route('/access_api/<string:end_point>', methods=["GET", "POST"])
@login_required
def access_api(end_point):
    global cities
    user = current_user.username
    url = "http://127.0.0.1:5001/"
    if request.method == "POST":
        if end_point == 'review':
            supp = request.form.get('supp')
            rev = request.form.get('rev-input')
            rat = request.form.get('rate')
            data = json.dumps({'uname': user, 'supp': supp, 'rev': rev, 'rating': rat})
            print(data)
            res = requests.post(url + 'reviews/add_review', json=data, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
        if end_point == 'loc':
            detail = request.args.get('loc').split(':')
            change = request.form.get('data')
            item = "equipment" if detail.pop(0) == "eq" else "material"
            ep = detail.pop(0)
            if 'remove' in ep:
                change = change[:-2].split(', ')
                data = json.dumps({'uname': user, 'detail': detail[0], 'change': change})
                res = json.loads(requests.delete(url + f'item/{item}', json=data).json())
                print(res)
                return "Done"
            ep = ep.split('_')[1]
            if 'Price' in ep:
                change += request.form.get('input')
            data = {'uname': user, 'detail': detail[0], 'change': change}
            print(data, ep, item)
            res = requests.post(url + f'change/{ep}/{item}', data=data)
            res = json.loads(res.json())
        #print(res)
        return "<h1>Done</h1>"
    if end_point == "loc":
        req = request.args.get('loc').split(':')
        if 'eq' in req:
            res = requests.get(url + 'item/equipment',
                    params={'user': user, 'locations': req[2]}).json()
        else:
            res = requests.get(url + "item/material",
                    params={'user': user, 'locations': req[2]}).json()
        print(res)
        if 'review' in req:
            return render_template('review.html', items=json.loads(res), data=(user, req[2]))
        if 'Change' in req[1]:
            return render_template('update_or_review.html', cities=cities, items=json.loads(res), data=(user, req[2]))
        if 'remove' in req[1]:
            return render_template('review.html', items=json.loads(res), data=(user, req[2]))
    
    if end_point == 'review':
        res = requests.get(url + f'history/{user}')
        history = json.loads(res.json())
        return render_template('upload_review.html', history=history)

    if end_point == 'complaints':
        res = requests.get(url + "history",
                params={'user': user})
        history = json.loads(res.json())
        return render_template('upload_review.html', history=history)


        
        return "<h1>done</h1>"
    
    #return "<h1>done</h1>"

#@views.route('/remove')
#def remove():






@views.route('/check')
def check():
    return render_template("check.html")


#!/usr/bin/env python3
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



@views.route('/query', methods=["POST", "GET"])
def query():
    query = json.loads(request.args.get('query1'))
    loc = request.args.get('loc').split('/')
    item = loc[0]
    print(item)
    loc = {"name": loc[1], "sub_city": loc[2], "city": loc[3]}
    if request.method == "POST":
        bookings = request.form.get('supp')
        if bookings:
            bookings = bookings[:-2]
        bookings = bookings.split(', ')
        uname = current_user.username
        if item == "E":
            coll = ['EquipmentSuppliers', 'equipment']
        else:
            coll = ['MaterialSuppliers', 'material']
        for book in bookings:
            details = book.split('-')
            engine.update({'coll': coll[0], 'row': {'username': details[0]}, 'update1': {"$set": { "locations.$[ln].equipments.$[eq].available": False } }, "array_filters": [ {"ln.name": loc['name'], "ln.city": loc['city'], "ln.sub_city": loc['sub_city'] }, {"eq.name": details[1]} ] })
            engine.update({'coll': 'User', 'row': {'username': details[0]}, 'update1': { "$inc": { "notifications.num": 1 }}})
            
            booking = { 'Booking': {"username": details[0], "location": ('-').join(loc.values()), "name": details[1] } }
            booked =  { 'Booking': {"username": uname, "location": ('-').join(loc.values()),"name": details[1] } }
            engine.init_validate(booking)
            engine.init_validate(booked)
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': {"$push":  {f"{coll[1]}_bookings": { "$each": [booking['Booking']] } } } })
            engine.update({'coll': coll[0], 'row': {'username': details[0]}, 'update1': {"$push":  {f"booked_{coll[1]}s": { "$each": [booked['Booking']] } } } })
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 } } })
        flash(f"Equipment succesfully booked", "success")
        return "<h1>Done!<\h1>"
        #return redirect(url_for("views.welcome"))
    return render_template("queries.html", query=query)



@views.route('/user-login', methods=["POST", "GET"])
@login_required
def welcome():
    locations = ["Total", "Mexico", "Piassa"]
    nots = engine.find({'coll': 'User', 'find': {'username': current_user.username}, 'fields': {"notifications": 1, "_id": 0} } )
    if request.method == "POST":
        city = request.form.get('city')
        sub_city = request.form.get('sub-city')
        location = request.form.get('location')
        equipment = request.form.get('equipment') 
        return redirect(url_for('views.query', query=query))
        

        #print(city, sub_city, location, equipment)
    return render_template("welcome.html", cities=cities, equipments=equipments, locations=locations, nots=nots)

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




@views.route('/book', methods=["POST", "GET"])
@login_required
def book():
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]
    materials = ["Sand", "Steel", "Aggregate", "Cement"]

    if request.method == "POST":
        item = request.form.get('item')
        print(item)
        city = request.form.get('city')
        sub_city = request.form.get('sub-city').split('/')[1]
        location = request.form.get('location')
        equipments = request.form.get('equipment').split(' ')
        print(city, sub_city, location, equipments)
        query1 = engine.find({'coll': 'EquipmentSuppliers', 'agg': [{"$unwind": "$locations"}, {"$unwind": "$locations.equipments"}, {"$match": {"locations.name": location, "locations.city": city, "locations.sub_city": sub_city, "locations.equipments.machine": { "$in": equipments } } }, {"$project": {"_id": 0, "available": 0, "locations.name": 0, "locations.sub_city": 0, "locations.city": 0, "locations.equipments.available":  0, "locations.equipments.back_up": 0, "equipments": 0, "available": 0} }] })
        #print(query1)
        loc = f"{item}/{location}/{sub_city}/{city}"
        return redirect(url_for('views.query', query1=json.dumps(query1), loc=loc))
    if request.method == "GET" and request.args.get('item') == 'equip':
        items = ('Equipment(s)', equipments)
        #print(request.args.get('item'))
    else:
        items = ('Material(s)', materials)
    #print(items[0][0])
    return render_template('book.html', cities=cities, items=items)



@views.route('/become_supp', methods=["POST", "GET"])
@login_required
def become_supp():
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]
    materials = ["Sand", "Steel", "Aggregate", "Cement"]
    if request.method == "POST":
        item = request.form.get('item')
        city = request.form.get('city')
        sub_city = request.form.get('sub-city').split('/')[1]
        location = request.form.get('location')
        equipments = request.form.get('equipment').split(', ')
        uname = current_user.username
        for machine in equipments:
            for j in range(int(i[-1])):
                pass
        #engine.add_new({'coll': 'EquipmentSuppliers', 'row': {"uername": uname, "locations": {"name": location, "city": city, "sub_city": sub_city, "equipments": [{"machine": machine, "name": f"{machine}{j + 1}"}, }))
        #print(item, city, sub_city, location, equipments)
        return "<h1>Done</h1>"
        #return redirect(url_for('views.query', query1=json.dumps(query1), loc=loc))
    if request.method == "GET" and request.args.get('item') == 'equip_supp':
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
    #print(request.args)
    user = current_user.username
    url = "http://127.0.0.1:5001/"
    if request.method == "POST":
        if end_point == ('review'):
            supp = request.form.get('supp')
            rev = request.form.get('rev')
            rat = request.form.get('rat')
            data ={'uname': user, 'supp': supp, 'rev': rev, 'rating': rat}
            res = requests.post(url + 'reviews/add_review', data=data)
        else:
            pass
        return "<h1>Done</h1>"
    if end_point == "loc":
        req = request.args.get('loc').split(':')
        #print(req[1])
        if 'eq' in req:
            res = requests.get(url + 'item/equipment',
                    params={'user': user, 'locations': req[2]}).json()
        else:
            res = requests.get(url + "item/material",
                    params={'user': user, 'locations': req[2]}).json()
        items = json.loads(res)[0].get('locations')[0].get('equipments')
        if 'review' in req:
            return render_template('review.html', items=items, data=(user, req[2]))
        return render_template('update_or_review.html', items=items)
    
    if end_point == 'review':
        print(request.args.get('history'))
        res = requests.get("http://127.0.0.1:5001/history",
                params={'user': user})
        history = json.loads(res.json())
        print(history)
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


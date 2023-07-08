#!/usr/bin/env python3
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from models.engine import engine
from models.data.users import User
import json
import requests
import os




views = Blueprint('views', __name__)
cities = {'Addis': {'subcities': {'Kolfe': {'locations': ['tor-hailoch', 'ayer-tena']}, 'lafto': { 'locations': ['weyra', 'akaki']}, 'kaliit': { 'locations': ['total', 'mexico', 'golf-club']}}}, 'Hawassa': {'subcities': {'Atote': {'locations': ['tor-hailoch', 'ayer-tena']}, 'Harar-sefer': { 'locations': ['weyra', 'akaki']}, 'Piassa': { 'locations': ['total', 'mexico', 'golf-club']}}}}



@views.route('/')
@login_required
def home():
    return render_template("home.html")



@views.route('/query/<string:item>', methods=["POST", "GET"])
def query(item):
    query = json.loads(request.args.get('query1'))
    print(query)
    #print(query[0]['locations']['items'])
    loc = request.args.get('loc').split('/')
    loc = {"name": loc[0], "sub_city": loc[1], "city": loc[2]}
    if request.method == "POST":
        print('hello')
        bookings = request.form.get('supp')
        if bookings:
            bookings = bookings[:-2].split(', ')
        uname = current_user.username
        coll = 'EquipmentSuppliers' if item == "equipment" else 'MaterialSuppliers'
        for book in bookings:
            details = book.split('-')

            print(book, details, bookings, loc, item)
            engine.update({'coll': coll, 'row': {'username': details[0]}, 'update1': {"$set": { "locations.$[ln].items.$[it].available": False } }, "array_filters": [ {"ln.name": loc['name'], "ln.city": loc['city'], "ln.sub_city": loc['sub_city'] }, {"it.name": details[1]} ] })
            engine.update({'coll': 'User', 'row': {'username': details[0]}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": {"$each": [f"One of your {item}s have been booked"], "$position": 0 } } } })
            
            days = 1 if item == 'material' else int(request.args.get('days'))
            booking = {"username": details[0], "location": ('/').join(loc.values()), 'item': item , "name": details[1], 'date': datetime.utcnow()}
            booking['return_date'] = booking['date'] + timedelta(days=days)
            booked = booking.copy()
            booked["username"] = uname
            print(booking)
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': {"$push":  {f"{item}_bookings": booking } } } )
            engine.update({'coll': coll, 'row': {'username': details[0]}, 'update1': {"$push":  {f"booked_{item}s": booked } } })
            engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": {"$each": [f"You have successfully booked a {item}"], "$position": 0 } } } })
        flash(f"Please feel free to add other bookings", "success")
        return redirect(url_for('views.book', item=item))
        #return redirect(url_for("views.welcome"))
    print(query)
    return render_template("queries.html", query=query)



@views.route('/user-login', methods=["POST", "GET"])
@login_required
def welcome():
    locations = ["Total", "Mexico", "Piassa"]
    uname = current_user.username
    #nots = engine.find({'coll': 'User', 'find': {'username': current_user.username}, 'fields': {"notifications": 1, "_id": 0} } )
    print(uname)
    nots = engine.find({'coll': 'User', 'find': {'username': uname}, 'fields': {"_id": 0, "notifications.num": 1} })[0]['notifications']['num']
    if request.method == "POST":
        city = request.form.get('city')
        sub_city = request.form.get('sub-city')
        location = request.form.get('location')
        equipment = request.form.get('equipment') 
        return redirect(url_for('views.query', query=query, loc=loc))
        

        #print(city, sub_city, location, equipment)
    engine.feed_history(current_user.username)
    return render_template("welcome.html", cities=cities, equipments=equipments, nots=int(nots), uname=current_user.username)

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
    uname = current_user.username
    equipments = ["Mixer", "Vibrator", "Compactor", "Excavator"]
    materials = ["Sand", "Steel", "Aggregate", "Cement"]

    if request.method == "POST":
        try:
            if item == 'equipment':
                coll = 'EquipmentSuppliers'
                selector = "machine"
            else:
                coll = 'MaterialSuppliers'
                selector = "name"
            city = request.form.get('city')
            sub_city = request.form.get('sub-city')
            location = request.form.get('location')
            eqs = request.form.get('equipment')
            if not (city and sub_city and location and eqs and request.form.get('days')):
                raise ValueError("fields not properly filled.")
            sub_city, eqs = sub_city.split('/')[1], eqs.split(', ')
            query1 = engine.find({'coll': coll, 'agg': [ {"$match": {"username": {"$not": {"$eq": uname}}}}, {"$unwind": "$locations"}, {"$unwind": "$locations.items"}, {"$match": {"locations.name": location, "locations.city": city, "locations.sub_city": sub_city, f"locations.items.{selector}": { "$in": eqs }, "locations.items.available": True } }, {"$project": {"_id": 0, "username": 1, "locations.items": 1, "contact_info": 1} }] })
            query1 = sorted(sorted(query1, key=lambda x: x['locations']['items'].get('name')), key=lambda x: x.get('username'))
            loc = f"{location}/{sub_city}/{city}"
            return redirect(url_for('views.query', item=item, query1=json.dumps(query1), loc=loc, days=request.form.get('days')))
        except Exception as e:
            flash(str(e), category='error')
    print(equipments)
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
        form = request.form
        coll = 'EquipmentSuppliers' if item == 'equipment' else 'MaterialSuppliers'
        city = form.get('city')
        sub_city = form.get('sub-city').split('/')[1]
        location = form.get('location')
        it_lst = [x for x in ['it1', 'it2', 'it3'] if form.get(x)]
        uname = current_user.username        
        values = []
        try:
            for it in it_lst:
                if not (form.get(f'{it}-price') and form.get(f'{it}-price').isdigit()):
                    raise ValueError(f"Price not properly filled for item {it[-1]}")
                if item == 'equipment' and not (form.get(f'{it}-yused') and form.get(f'{it}-yused').isdigit()):
                    raise ValueError(f"Years used not properly filled for item {it[-1]}")
            if type == 'new':
                if not (form.get('contactinfo') and  form.get('contactinfo')[:2] == '09' and form.get('contactinfo').isdigit() and len(form.get('contactinfo')) == 10):
                    raise ValueError(f"contact info not properly provided. please check the fileds corresponding to your contact info.")
                if engine.find({'coll': coll, 'find': {'username': uname}, 'fields': {}}):
                    raise ValueError(f"You are already registered as {item} Supplier, please use Add {item} option on the home page.")
            if type == 'add' and not engine.find({'coll': coll, 'find': {'username': uname}, 'fields': {}}):
                    raise ValueError(f"You aren't registered as {item} Supplier yet, please use Become {item} supplier option on the home page.")
            for it in it_lst:
                val = {'price': form.get(f'{it}-price'), 'name': form.get(it)}
                if item == "equipment":
                    val['years_used'] = form.get(f'{it}-yused')
                    val['machine'] = form.get(it)
                values += [val]
            dct = {"coll": coll, 'username': uname, 'filter':
                    {'name': location, 'sub_city': sub_city,
                    'city': city}, 'append': values}
            if type == 'new':
                dct['contact_info'] = form.get('contactinfo')
            items = engine.append_or_create(dct)
            if not items:
                raise ValueError("Similar materials can't be registerd in the same location.")
            for i in range(len(it_lst)):
                filename = f"{uname}_{location}_{sub_city}_{city}_{items[i]}.jpg"
                basedir = os.path.abspath(os.path.dirname(__file__))
                f = request.files[f'{it_lst[i]}cred']
                f.save(os.path.join(basedir, f'static/images/verification/{item}', filename))
            for i in it_lst:
                engine.update({'coll': 'User', 'row': {'username': uname}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully registered a {item}"], "$position": 0 } } } })
            flash(f"Please check your {item} list", category="success")
        except ValueError as e:
            print(e)
            flash(str(e), category='error')
        return redirect(request.url)
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
            res = requests.post(url + 'reviews/add_review', json=data, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
            engine.update({'coll': 'User', 'row': {'username': user}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully submitted a review"], "$position": 0 } } } })
        if end_point == 'loc':
            detail = request.args.get('loc').split(':')
            change = request.form.get('data')
            item = "equipment" if detail.pop(0) == "eq" else "material"
            ep = detail.pop(0)
            if 'remove' in ep:
                change = change[:-2].split(', ')
                data = json.dumps({'uname': user, 'detail': detail[0], 'change': change})
                res = json.loads(requests.delete(url + f'item/{item}', json=data).json())
                engine.update({'coll': 'User', 'row': {'username': user}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully removed an {item}"], "$position": 0 } } } })
                return redirect(request.url)
            ep = ep.split('_')[1]
            if 'Price' in ep:
                change += request.form.get('input')
            data = {'uname': user, 'detail': detail[0], 'change': change}
            res = requests.post(url + f'change/{ep}/{item}', data=data)
            res = json.loads(res.json())
            engine.update({'coll': 'User', 'row': {'username': user}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully changed the {ep} of a {item}"], "$position": 0 } } } })
            return redirect(request.url)
    if end_point == "loc":
        req = request.args.get('loc').split(':')
        if 'eq' in req:
            res = requests.get(url + 'item/equipment',
                    params={'user': user, 'locations': req[2]}).json()
        else:
            res = requests.get(url + "item/material",
                    params={'user': user, 'locations': req[2]}).json()
            res = sorted(sorted(json.loads(res), key=lambda x: x.get('name')), key=lambda x: x.get('username'))
        if 'review' in req:
            return render_template('review_or_remove.html', items=res, data=(user, req[2]))
        if 'Change' in req[1]:
            return render_template('update_or_review.html', cities=cities, items=res, data=(user, req[2]))
        if 'remove' in req[1]:
            return render_template('review_or_remove.html', items=res, data=(user, req[2]))
    
    if end_point == 'review':
        res = requests.get(url + f'history/{user}')
        history = sorted(sorted(json.loads(res.json()), key=lambda x: x.get('name')), key=lambda x: x.get('username'))
        return render_template('upload_review.html', history=history)

    if end_point == 'complaints':
        res = requests.get(url + "history",
                params={'user': user})
        history = json.loads(res.json())
        return render_template('upload_review.html', history=history)

    

@views.route('/view/<string:item>', methods=["POST", "GET"])
def view(item):
    if request.method == "POST":
        if item == 'bookings':
            input = request.form.get('input').split(':')
            coll = 'EquipmentSuppliers' if input[2] == 'equipment' else 'MaterialSuppliers'
            loc = input[0].split('/')
            place, sub_city, city = loc[0], loc[1], loc[2]
            print(input)
            if input[2] == 'equipment':
                engine.update({'coll': coll,'row': {'username': input[1]}, 'update1':{"$set": {"locations.$[l].items.$[i].available": True}}, 'array_filters': [{'l.name': loc[0], 'l.sub_city': loc[1], 'l.city': loc[2]}, {'i.name': input[3]}]})
            engine.update({'coll': 'User', 'row': {"username": current_user.username}, 'update1': {"$pull":  {f"{input[2]}_bookings": {"location": input[0], "name": input[3] } } } })
            engine.update({'coll': coll, 'row': {"username": input[1]}, 'update1': {"$pull":  {f"booked_{input[2]}s": {"location": input[0], "name": input[3] } } } })
            engine.update({'coll': 'User', 'row': {'username': current_user.username}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"You have successfully removed a {input[2]} booking"], "$position": 0 } } } })
            engine.update({'coll': 'User', 'row': {'username': input[1]}, 'update1': { "$inc": { "notifications.num": 1 }, "$push": {"notifications.notes": { "$each": [f"A {input[2]} booking from {current_user.username} has been removed"], "$position": 0 } } } })
        return redirect(request.url)
    find = {'username': current_user.username}
    if item == 'bookings':
        bookings = engine.find({'coll': 'User', 'find': find, 'fields': {'equipment_bookings': 1, 'material_bookings': 1, '_id': 0} })[0]
        bookings['material_bookings'].extend(bookings['equipment_bookings'])
        bookings = bookings['material_bookings']
        data = bookings
    elif item == 'equipments' or item == 'materials':
        coll = 'EquipmentSuppliers' if item[0] == 'e' else 'MaterialSuppliers'
        data = engine.find({'coll': coll, 'find': find, 'fields': {'locations': 1, '_id': 0} })
        if data:
            data = data[0]['locations']
            for loc in data:
                loc['name'] += '/' + loc['sub_city'] + '/' + loc['city']
                loc.pop('city', None)
                loc.pop('sub_city', None)
    elif item == "history":
        data = engine.find({'coll': 'User', 'find': find, 'fields': {'history': 1, '_id': 0} })[0]['history']
    elif item == "booked":
        booked_eq = engine.find({'coll': 'EquipmentSuppliers', 'find': {'username': current_user.username}, 'fields': {'booked_equipments': 1, '_id': 0} }) 
        if booked_eq:
            booked_eq = booked_eq[0]['booked_equipments']
        booked_eq = sorted(sorted(booked_eq, key=lambda x: x.get('name')), key=lambda x: x.get('usrename'))
        booked_mt = engine.find({'coll': 'MaterialSuppliers', 'find': {'username': current_user.username}, 'fields': {'booked_materials': 1, '_id': 0} })
        if booked_mt:
            booked_mt = booked_mt[0]['booked_materials']
        booked_mt = sorted(sorted(booked_mt, key=lambda x: x.get('name')), key=lambda x: x.get('usrename'))
        return render_template('booked.html', data=(booked_eq, booked_mt))
    if item == 'equipments' or item == 'materials':
        data.sort()
        for loc in data:
            loc['items'] = sorted(loc['items'], key=lambda x: x.get('name'))
    else:
        data = sorted(sorted(data, key=lambda x: x.get('name')), key=lambda x: x.get('date'), reverse=True)
    return render_template('bookings_and_items.html', data=data)



def restrict_ips(func):
    def wrapper(*args, **kwargs):
        if '192' in request.remote_addr[:3]:
            abort(403)
        return func(*args, **kwargs)
    return wrapper



@views.route('/validate/<string:option>', methods=["POST", "GET"])
@restrict_ips
def check(option):
    if request.method == "POST":
        val = request.form.get('input')
        try:
            raise(ValidationError)
            flash(f"{option} successfuly done", category='success')
        except Exception:
            flash("operation did not succesfuly completed!", category="danger")
        return redirect(request.url)
    coll = 'ValItem' if option == 'item' else 'ValSupp'
    validate = engine.find({'coll': coll, 'find': {}, 'fields': {}})
    return render_template("validate.html", validate=validate)


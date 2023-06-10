#!/usr/bin/env python3
from flask import (Blueprint, render_template,
        request, flash, redirect, url_for, session)
from flask_login import login_user, login_required, logout_user, current_user
from .forms import register_form, login_form
from models.engine import setup_connection
from models.data.users import User



auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = login_form(meta={'csrf': False})
    if request.method == 'POST':
        if form.validate_on_submit():
            flash(f"Successfully Logged in!", "success")
            user = User.objects(email=form.email.data).first()
            login_user(user)
            return redirect(url_for('views.welcome'))
    return render_template("auth.html", form=form)

@auth.route('/logout')
@login_required
def logout():
    return "<p>Logout</p>"

@auth.route('/sign-up/', methods=['GET', 'POST'])
def sign_up():
    form = register_form(meta={'csrf': False})
    if request.method == 'POST':
        print('Hello')
        print(form.validate_on_submit())
        if form.validate_on_submit():
            print('Hallo')
            try:
                email = form.email.data
                password = form.pwd.data
                username = form.username.data
                User(email=email, password=password, username=username).save()
                flash(f"Account successfly created", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(e, "danger")
    return render_template("auth.html", form=form)



'''form = register_form()
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if len(email) < 4:
            flash('email must be greater than 3 characters', category='error')
        elif len(firstName) < 2:
            flash('firstname should be at least 2 characters', category='error')
        elif len(lastName) < 2:
            flash('lastname shoud be at least 2 characters', category='error')

        elif len(password1) < 7:
            flash('passord must be atleast 7 characters', category='error')
         elif password1 != password2:
            flash('passwords don\'t match', category='error')
        else:
            flash('Account created', category='success')

        dct = {'email': email, 'firstName': firstName, 'lastName': lastName, 'password': password1}
        db.users.insert_one(dct)
        
email = request.form.get('email')
        password = request.form.get('password1')
        chk_email = db.users.find_one({'email': email})
        if not chk_email:
            flash(you have not signed up, email not found', category='error)
        elif chk_email and password != chk_email['password']:
            flash(you have entered wrong password, category=error)
        return <p>Welcome</p>
        '''


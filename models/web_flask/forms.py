#!/usr/bin/env python3

from wtforms import (
        StringField,
        PasswordField,
        BooleanField,
        IntegerField,
        DateField,
        TextAreaField,
        )
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp, Optional
import email_validator
from flask_login import current_user
from wtforms import ValidationError, validators
from models.data.users import User
from models.engine import setup_connection


class login_form(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(6, 64)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=72)])
    #username = StringField(validator=[InputRequired()])

    def validate_email(self, email):
        collec = User._get_collection()
        if not collec.find_one({'email': email.data}):
            raise ValidationError('Account not found')

    def validate_password(self, password):
        collec = User._get_collection().find_one({'email': self.email.data})
        if collec and password.data != collec['password']:
            raise ValidationError('Wrong password')

class register_form(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(3, 17, message="please provide a valid name"),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Usernames must have only letters, " "numbers, dots or underscores",),])
    email = StringField(validators=[InputRequired(), Email(), Length(4, 64)])
    pwd = PasswordField(validators=[InputRequired(), Length(8, 72)])
    cpwd = PasswordField(validators=[InputRequired(),
                                     Length(8, 72),
                                     EqualTo("pwd", message="passwords must match!")])

    def validate_email(self, email):
        collec = User._get_collection()
        print(collec.find_one({'email': email.data}))
        if collec.find_one({'email': email.data}):
            raise ValidationError("Email already registered!")

    def validate_username(self, username):
        collec = User._get_collection()
        print(username.data)
        if collec.find_one({'username': username.data}):
            raise ValidationError("Username already taken!")

    

#volcano27!

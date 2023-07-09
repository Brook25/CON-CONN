#!/usr/bin/env python3

from mongoengine import connect

connect(db='my_db', alias='cnn')

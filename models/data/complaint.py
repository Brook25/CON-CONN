#!/usr/bin/env python3
import mongoengine


class Complaint(mongoengine.EmbeddedDocument):
    user_id = mongoengine.StringField(required=True)
    complaint = mongoengine.StringField(required=True)
    

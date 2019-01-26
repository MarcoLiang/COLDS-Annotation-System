from schema import db

class Class(db.Document):
    owner_id = db.ReferenceField('User', required=True)
    owner_name = db.StringField(required=True)
    name = db.StringField(required=True)

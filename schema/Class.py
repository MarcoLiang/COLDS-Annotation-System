from schema import db

class Class(db.Document):
    owner = db.ReferenceField('User', required=True)
    name = db.StringField(required=True)

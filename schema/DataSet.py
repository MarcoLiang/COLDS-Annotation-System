from schema import db


class Dataset(db.DynamicDocument):
    name = db.StringField(required=True)
    owner = db.ReferenceField("User",required=True)
    privacy = db.StringField(required=True)
    collaborators = db.ListField(db.ReferenceField('User'))

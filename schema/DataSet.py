from schema import db


class Dataset(db.DynamicDocument):
    ds_name = db.StringField(required=True)
    author = db.ReferenceField("User",required=True)
    privacy = db.StringField(required=True)
    collaborators = db.ListField(db.ReferenceField('User'))

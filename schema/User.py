from schema import db

class User(db.DynamicDocument):
    gitlab_id = db.IntField(require=True, unique=True)
    name = db.StringField(required=True)
    email = db.StringField(required=True, unique=True)

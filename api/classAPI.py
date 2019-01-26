from flask import make_response, render_template, current_app, jsonify, session
from flask_restful import Resource, reqparse
from schema.Class import Class
from schema.User import User
from util.userAuth import login_auth_required

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('password', type=str)
parser.add_argument('instructor', type=str)

class ClassAPI(Resource):
    @login_auth_required
    def post(self):
        headers = {'Content-Type': 'application/json'}
        user = User.objects(id=session['user_id']).first()

        args = parser.parse_args()

        class_ = Class()
        class_.owner_id = user.id
        class_.owner_name = user.name
        class_.name = args['name']
        class_.save()

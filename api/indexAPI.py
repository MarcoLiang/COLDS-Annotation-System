from flask import redirect, make_response, render_template, session
from flask_restful import Resource, reqparse
from schema.User import User
from util.userAuth import login_auth_required


class IndexAPI(Resource):
    def get(self):
        return make_response(
            render_template("index.html", logged_in=('user_id' in session)),
            200,
            {'Content-Type': 'text/html'}
        )

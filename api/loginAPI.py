from flask import make_response, render_template, current_app, redirect, jsonify, abort, session
from flask_restful import Resource, reqparse
from mongoengine.errors import NotUniqueError, ValidationError
from util.userAuth import login_auth_required
from schema.User import User
from util.exception import InvalidUsage
import json
import os


userParser = reqparse.RequestParser()
userParser.add_argument('name', type=str)
userParser.add_argument('password', type=str)
userParser.add_argument('email', type=str)
userParser.add_argument('group', type=str)

class LoginAPI(Resource):
    @login_auth_required
    def get(self):
        token = session['gitlab_token']
        user = gitlab.get(token)
        return jsonify(user.data)

        if user.group == "instructor":
            return redirect("/instructor")
        elif user.group == "annotator":
            return redirect("/annotator")

    def post(self):
        ## login with GitLab
        

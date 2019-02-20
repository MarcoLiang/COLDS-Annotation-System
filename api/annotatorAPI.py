from flask import make_response, render_template, current_app, jsonify, session
from flask_restful import Resource, reqparse
from util.userAuth import login_auth_required

from schema.User import User
from schema.Query import Query
from schema.Assignment import Assignment

parser = reqparse.RequestParser()


class AnnotatorAPI(Resource):
    @login_auth_required
    def get(self):
        headers = {'Content-Type': 'text/html'}

        user_id = session['user_id'];
        user = User.objects(id=user_id).first()

        assignments = Assignment.objects()

        for assignment in assignments:
            assignment['owner_name'] = assignment.owner.name
            assignment['owner_id'] = str(assignment.owner.id)
            assignment['ds_name'] = assignment.dataset.name
            assignment['complete'] = assignment.statuses.get(str(user_id), False)

        return make_response(
            render_template(
                "annotator.html",
                data={
                    "assignments" : assignments,
                    "user" : user
                }, 
                logged_in=('user_id' in session)
            ),
            200, 
            headers
        )

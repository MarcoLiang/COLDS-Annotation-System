from flask import make_response, jsonify, current_app, request, render_template, session
from flask_restful import Resource, reqparse
from flask_paginate import Pagination, get_page_parameter

from schema.User import User
from schema.Dataset import Dataset
from schema.Assignment import Assignment
from schema.Annotation import Annotation
from schema.Document import Document
from schema.Query import Query
from schema.Class import Class

from util.userAuth import login_auth_required
from util.exception import InvalidUsage
import os, json

class InstructorAPI(Resource):
    @login_auth_required
    def get(self):
        user = User.objects(id=session['user_id']).first()

        my_datasets = Dataset.objects(owner=user)
        public_datasets = Dataset.objects(privacy='public', owner__ne=user)
        authorized_datasets = Dataset.objects(privacy='private', collaborators__in=[user])

        classes = [class_.name for class_ in Class.objects(owner=user)]
        assignments = list(map(self._collect_assignment_data, Assignment.objects(owner=user)))  

        return make_response(render_template(
                "instructor.html", 
                data={
                    "user" : json.dumps(user.to_json()),
                    "my_datasets" : my_datasets,
                    "public_datasets" : public_datasets,
                    "authorized_datasets" : authorized_datasets,
                    "classes" : classes,
                    "assignments" : assignments
                },
                logged_in=('user_id' in session)
            ), 
            200, 
            {'Content-Type': 'text/html'}
        )


    def _collect_assignment_data(self, assignment):
        assignment.queries = Query.objects(assignment=assignment)
        assignment.ds_name = assignment.dataset.name
        assignment.owner_id = str(assignment.owner.id)
        return assignment
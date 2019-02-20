from flask import make_response, render_template, session, jsonify, redirect, current_app
from flask_restful import Resource, reqparse
from schema.Dataset import Dataset

from schema.User import User
from schema.Query import Query
from schema.Assignment import Assignment
import os, metapy

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('dataset', type=str)
parser.add_argument('query', type=str)
parser.add_argument('ranker', type=str)
parser.add_argument('params', type=dict)
parser.add_argument('deadline', type=str)
parser.add_argument('status', type=bool)
parser.add_argument('content', type=str)
parser.add_argument('creator', type=str)
parser.add_argument('doc_scores', type=dict)
parser.add_argument('num_results', type=int)


class AssignAPI(Resource):
    def post(self):
        headers = {'Content-Type': 'application/json'}
        args = parser.parse_args()
        name = args['name']
        ranker = args['ranker']
        params = args['params']
        dataset = args['dataset']
        deadline = args['deadline']
        doc_scores = args['doc_scores']
        num_results = args['num_results']
 
        assignment = Assignment()
        assignment.name = name
        assignment.owner = User.objects(id=session['user_id']).first()
        assignment.ranker = ranker
        assignment.params = params
        assignment.dataset = Dataset.objects(id=dataset).first()
        assignment.annotators = User.objects()
        assignment.statuses = {str(anno.id): False for anno in assignment.annotators}
        assignment.deadline = deadline
        assignment.num_results = num_results
        assignment.save()

        return str(assignment.id)


class AssignmentAPI(Resource):
    def get(self, owner_id, assignment_name):
        headers = {'Content-Type': 'text/html'}
        args = parser.parse_args()
        owner = User.objects(id=owner_id).first()
        user_id = session['user_id']
        user = User.objects(id=user_id).first()

        assignment = Assignment.objects(name=assignment_name)  \
            .filter(owner=owner).first()

        # Allow re-submission
        #if assignment.statuses[str(user_id)]:
        #    return redirect("/annotator")

        assignment.owner_name = assignment.owner.name
        assignment.ds_name = assignment.dataset.name
        assignment.ds_owner_id = str(assignment.dataset.owner.id)

        queries = Query.objects(assignment=assignment, creator=user, submitted=False)
        return make_response(
            render_template(
                "assignment.html",
                user = user,
                assignment = assignment,
                queries = queries
            ),
            200,headers)


parser.add_argument('assignment_id', type=str)

class AssignmentUpdateAPI(Resource):
    def post(self):
        args = parser.parse_args()
        assignment_id = args['assignment_id']

        assignment = Assignment.objects(id=assignment_id).first()

        name = args['name']
        query = args['query']
        ranker = args['ranker']
        params = args['params']
        dataset = args['dataset']
        deadline = args['deadline']
        doc_scores = args['doc_scores']

        assignment.name = name
        assignment.query = query
        assignment.ranker = ranker
        assignment.params = params
        assignment.deadline = deadline

        if len(doc_scores) != 0:
            assignment.doc_scores = doc_scores
 
        assignment.save()

        return jsonify(assignment)


class AddQueryAPI(Resource):
    def post(self):
        headers = {'Content-Type': 'application/json'}
        args = parser.parse_args()
        content = args['content']
        dataset = args['dataset']
        creator = args['creator']
        dataset = Dataset.objects(id=dataset)
        creator = User.objects(id=creator)
        query = Query()
        query.content = content
        query.data_set = dataset[0]
        query.creator = creator[0]
        query.submitted = False
        query.save()
        return make_response(jsonify("succeed"), 200, headers)

from flask import make_response, render_template, current_app, jsonify
from flask_restful import Resource, reqparse
from search.searcher import Searcher
from schema.User import User
import os, json

env = os.environ["APP_ENV"]
cfg = json.loads(open('config.json').read())[env]

parser = reqparse.RequestParser()
parser.add_argument('query', type=str)
parser.add_argument('ranker', type=str)
parser.add_argument('num_results', type=int)
parser.add_argument('params', type=dict)


class SearchAPI(Resource):
	def get(self, owner_id, ds_name):
		args = parser.parse_args()
		headers = {'Content-Type': 'text/html'}
		return make_response(render_template('search.html', documents={}), 200, headers)

	def post(self, owner_id, ds_name):
		args = parser.parse_args()
		query = args['query']
		ranker = args['ranker']
		num_results = args['num_results']
		params = args['params']

		owner = User.objects(id=owner_id).first()

		path = cfg["anno_dataset_base_path"] + str(owner.gitlab_id)
		searcher = Searcher(ds_name, path)
		documents = jsonify(searcher.search(query, ranker, params, num_results))
		return make_response(documents)

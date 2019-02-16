from flask import make_response, render_template, current_app, jsonify, session
from flask_restful import Resource, reqparse

from schema.Dataset import Dataset

from schema.User import User
from schema.Query import Query
from schema.Assignment import Assignment

import os, json

env = os.environ["APP_ENV"]
cfg = json.loads(open('config.json').read())[env]

parser = reqparse.RequestParser()
parser.add_argument('ds_id', type=str)
parser.add_argument('ds_name', type=str)
parser.add_argument('ds_privacy', type=str)
parser.add_argument('collaborators', type=str, action='append')

class DatasetUpdateAPI(Resource):
    def post(self):
        args = parser.parse_args()
        ds_id = args['ds_id']
        ds_name = args['ds_name']
        ds_privacy = args['ds_privacy']
        collaborators = args['collaborators']

        ds = Dataset.objects(id=ds_id).first()

        user = User.objects(id=session['user_id']).first()

        if len(ds_name) > 0:
            old_ds_path = cfg["dataset_base_path"] + str(user.gitlab_id) + "/" + ds.name
            new_ds_path = cfg["dataset_base_path"] + str(user.gitlab_id) + "/" + ds_name
            os.rename(old_ds_path, new_ds_path)
            ds.name = ds_name

        if ds_privacy != "":
            ds.privacy = ds_privacy

        if ds.privacy == 'public':
            ds.save()
            return make_response(jsonify({'message':"This dataset is already public."}), 200)

        for collaborator in collaborators:
            collab = User.objects(email=collaborator).first()
            if not collab:
                return make_response(
                    jsonify(
                        {"message": "Collaborator" + collaborator + "doesn't exist"}
                    ), 200, headers
                )
            else:
                ds.collaborators.append(collab)

        ds.save()

        return make_response(jsonify({'message':"OK"}), 200)

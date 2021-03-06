from flask import Flask, jsonify
from flask_restful import Api
from schema import db
from schema.User import User
from api.indexAPI import IndexAPI
from api.searchAPI import SearchAPI
from api.annotationAPI import AnnotationAPI
from api.uploadAPI import UploadAPI
from api.assignmentAPI import AssignAPI, AssignmentAPI, AssignmentUpdateAPI
from api.documentAPI import DocumentAPI
from api.documentAPI import DocumentsAPI
from api.datasetupdateAPI import DatasetUpdateAPI
from api.instructorAPI import InstructorAPI
from api.annotatorAPI import AnnotatorAPI
from api.queryAPI import QueryAPI
from api.alertAPI import AlertAPI
from api.classAPI import ClassAPI
from api.extractAPI import ExtractAPI

from util.exception import InvalidUsage

from flask import render_template, url_for, session, redirect, make_response, current_app
from authlib.flask.client import OAuth
import requests, os

app = Flask(__name__, static_folder='static/', static_url_path='')
app.config["SECRET_KEY"] = "secret"

# db settings only need to be specified in production
# defaults are used in development
env = os.environ["APP_ENV"]
if env == "prod":
    app.config['MONGODB_SETTINGS'] = {
       'db': 'prod',
       'host': 'mongo'
    }

api = Api(app)

db.init_app(app)

oauth = OAuth(app)
gitlab = oauth.register('gitlab',
        api_base_url='https://lab.textdata.org/api/v4/',
        request_token_url=None,
        access_token_url='https://lab.textdata.org/oauth/token',
        authorize_url='https://lab.textdata.org/oauth/authorize',
        access_token_method='POST',
        client_id='c280164bebe03d2a8f9387ae2fe4093107de124987731808eaada7a925d41384',
        client_secret='29972c32fadaea9bc9fff82d5ad822d3bf8af20e7d38d8509e7fc7031a8a4889',
        client_kwargs={"scope": "api"}
    )

api.add_resource(IndexAPI, '/')
api.add_resource(SearchAPI, '/search/<string:owner_id>/<string:ds_name>')
api.add_resource(AnnotationAPI, '/annotation')
api.add_resource(UploadAPI, '/upload')

api.add_resource(AssignAPI, '/assign')
api.add_resource(AssignmentAPI, '/assignment/<string:owner_id>/<string:assignment_name>')
api.add_resource(AssignmentUpdateAPI, '/assignment_update')

api.add_resource(QueryAPI, '/query')

api.add_resource(DocumentsAPI, '/documents')
api.add_resource(DocumentAPI, '/document')

api.add_resource(InstructorAPI, '/instructor')
api.add_resource(AnnotatorAPI, '/annotator')
api.add_resource(ClassAPI, '/class')

api.add_resource(DatasetUpdateAPI, '/dataset_update')

api.add_resource(AlertAPI, '/alert/<string:url>/<string:message>')
api.add_resource(ExtractAPI, '/extract')


@app.route('/login', methods=["POST"])
def login():
    return gitlab.authorize_redirect(url_for('authorized', _external=True, _scheme='http'))


@app.route('/logout')
def logout():
    del session['gitlab_token']
    del session['user_id']
    return redirect('/')


@app.route('/login/authorize')
def authorized():
    token = gitlab.authorize_access_token()
    session['gitlab_token'] = token

    resp = requests.get(
        'https://lab.textdata.org/api/v4/user?access_token=' + token['access_token'] 
    )

    resp = resp.json()
    if 'id' in resp:
        user = User.objects(gitlab_id=resp['id']).first()
        if not user:
            user = User(
                    gitlab_id=resp['id'],
                    name=resp['name'],
                    email=resp['email']
                )
            user.save()

        session['user_id'] = str(user.id)

        return redirect('/')
    else:
        return redirect('/logout')


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
	response = jsonify(error.to_dict())
	response.status_code = error.status_code
	return response


if __name__ == '__main__':
    app.run(debug=True)

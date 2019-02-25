from flask import make_response, jsonify, current_app, request, render_template, session
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
from util.utils import allowed_file
from util.exception import InvalidUsage

from schema import db
from schema.Dataset import Dataset
from schema.User import User
from schema.Document import Document
from util.userAuth import login_auth_required

import os, json, zipfile

env = os.environ["APP_ENV"]
cfg = json.loads(open('config.json').read())[env]

parser = reqparse.RequestParser()
parser.add_argument('ds_name', type=str)
parser.add_argument('ds_privacy', type=str)

class UploadAPI(Resource):
	"""
	API class for dataset uploading and viewing
	"""
	@login_auth_required
	def get(self):
            return make_response(
                render_template(
                    'upload_file.html',
                    author=User.objects(id=session["user_id"]).first()
                ),
                200,
                {'Content-Type': 'text/html'}
            )

	@login_auth_required
	def post(self):
            args = parser.parse_args()
            ds_name = args['ds_name']
            ds_privacy = args['ds_privacy']

            uploaded_files = request.files.getlist("file")
            
            is_zipfile = \
                    len(uploaded_files) == 1 and \
                    uploaded_files[0].filename[-4:] == ".zip"

            if is_zipfile:
                zipfile = uploaded_files[0]

            if not is_zipfile:
                err = self._validate_files(uploaded_files)
                if err:
                    return make_response(jsonify(err), 200)
            
            owner = User.objects(id=session["user_id"]).first()
            owner_path = self._get_or_init_owner_path()
            err, ds_path = self._get_or_init_ds_path(owner_path, ds_name)

            if err:
                return make_response(jsonify(err), 200)

            self._save_dataset_files(uploaded_files, ds_path, is_zipfile)
            self._save_dataset_configs(ds_path)
            dataset = self._save_dataset_entry(ds_name, owner, ds_privacy)

            for fname in os.listdir(ds_path):
                document = Document()
                document.name = fname
                document.dataset = dataset
                document.save()

            return make_response(
                jsonify({"message": "Files have been successfully uploaded"}),
                200
            )


	def _validate_files(self, files):
	    for file in files:
		if not file or not allowed_file(file.filename):
		    return {
			"message": "File(s) format is(are) not correct"
		    }

	    return None


	def _get_or_init_owner_path(self):
            owner = User.objects(id=session["user_id"]).first()
            owner_path = cfg["anno_dataset_base_path"] + str(owner.gitlab_id)
            
            if not os.path.exists(owner_path):
                os.mkdir(owner_path)

            return owner_path


	def _get_or_init_ds_path(self, owner_path, ds_name):
            ds_path = owner_path + "/" + ds_name + "/"
            if os.path.isdir(ds_path):
                return { "message": "Dataset already exists" }, ds_path

            os.mkdir(ds_path)
            return None, ds_path


	def _save_dataset_entry(self, ds_name, owner, ds_privacy):
            ds = Dataset()
            ds.name = ds_name
            ds.owner = owner
            ds.privacy = ds_privacy 
            ds.save()
            return ds


	def _save_dataset_files(self, files, ds_path, is_zipfile):
            if not is_zipfile:
                for file in files:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(ds_path, filename))
            else:
                fzip = files[0]
                fzip.save('/tmp/' + fzip.filename)

                zip_ref = zipfile.ZipFile('/tmp/' + fzip.filename, 'r')
                for zip_info in zip_ref.infolist():
                    if zip_info.filename[-1] == '/':
                        continue
                    zip_info.filename = os.path.basename(zip_info.filename)
                    zip_ref.extract(zip_info, ds_path)
                
                zip_ref.close()
                os.remove('/tmp/' + fzip.filename)


	def _save_dataset_configs(self, ds_path):
            if len(os.listdir(ds_path)) != 0:
                file_corpus = open(ds_path + "/dataset-full-corpus.txt", "w")
                file_toml = open(ds_path + "/file.toml", "w")
                file_metadata = open(ds_path + "/metadata.data", "w")

                for file in os.listdir(ds_path):
                    if file[-3:] == "txt" and file != "dataset-full-corpus.txt":
                        file_corpus.write("[None] " + file + "\n")
                        file_metadata.write(file + " " + file[:-4] + "\n")

                file_toml.write("type = \"file-corpus\"" + "\n")
                file_toml.write("list = \"dataset\"")

                file_corpus.close()
                file_toml.close()
                file_metadata.close()

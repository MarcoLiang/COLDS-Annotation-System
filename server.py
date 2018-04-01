from flask import Flask, jsonify, redirect, url_for
from flask import render_template
from flask_cors import CORS
from flask_restful import Api
from flask_login import LoginManager, current_user, login_required
from api.annotationAPI import AnnotationAPI
from api.assignmentAPI import AssignmentAPI, AddQueryAPI
from api.instructorAPI import InstructorAPI
# from api.searchAPI import SearchAPI
from api.uploadAPI import UploadAPI
from api.userAPI import RegisterAPI, LoginAPI, LogoutAPI
from schema import db, redis_store, User
from util.exception import InvalidUsage

app = Flask(__name__, static_folder='static/', static_url_path='')
app.config.from_object('config')
api = Api(app)
CORS(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main'


@login_manager.user_loader
def load_user(user_id):
    return User.User.objects(pk=user_id).first()


db.init_app(app)

api.add_resource(RegisterAPI, '/register')
api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')


# api.add_resource(SearchAPI, '/search/<string:author>/<string:ds_name>')
api.add_resource(AnnotationAPI, '/annotation')
api.add_resource(UploadAPI, '/upload')
api.add_resource(AssignmentAPI, '/assign')
api.add_resource(AddQueryAPI, '/newquery')
api.add_resource(InstructorAPI, '/instructor')


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def main():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1')

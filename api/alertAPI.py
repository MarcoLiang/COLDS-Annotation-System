from flask import make_response, render_template, current_app, jsonify, request, session
from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()

class AlertAPI(Resource):
	def get(self, url, message):
		return make_response(
			render_template('notification.html', 
				data={"url": "/" + url, "message": message}
			),
			200,
			{'Content-Type': 'text/html'}
		)
from flask import abort, current_app, request, session, redirect, render_template, make_response
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from functools import wraps
from schema.User import User

def login_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'gitlab_token' not in session:
            return redirect('/')

        return f(*args, **kwargs)
        
    return decorated_function

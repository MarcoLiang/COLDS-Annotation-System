from flask_oauthlib.client import OAuth

class GitLabAuth:

    def __init__(self, app):
        oauth = OAuth(app)
        self.gitlab = oauth.remote_app('gitlab',
                base_url='https://lab.textdata.org/api/v4/',
                request_token_url=None,
                access_token_url='https://lab.textdata.org/oauth/token',
                authorize_url='https://lab.textdata.org/oauth/authorize',
                access_token_method='POST',
                consumer_key='c280164bebe03d2a8f9387ae2fe4093107de124987731808eaada7a925d41384',
                consumer_secret='29972c32fadaea9bc9fff82d5ad822d3bf8af20e7d38d8509e7fc7031a8a4889'
            )

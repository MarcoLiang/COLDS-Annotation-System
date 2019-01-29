## Dataset Annotation Engine
The dataset annotation engine is an application originally created by a handful of graduate student over the past couple of years. It provides functionality for inserting a dataset into a search engine and allowing students to perform queries on the search engine, marking the returned documents as relevant or not relevant to the query. This allows new datasets to be developed, annotated, and used for new information retrieval experiments. The current work on the dataset annotation engine is to convert it to be supported with the Azure system used for hosting the other LiveDataLab services. This will allow it to pull datasets stored in the Azure file system, label those datasets, and utilize those datasets for new student assignments and research. While the initial application was functioning, there is a non-insignificant amount of work that needs to be done on it to get it ready to be run and used in a production environment.

The repository for the application can be found here: https://github.com/TIMAN-group/COLDS-Annotation-System.

### Architecture

The dataset annotation engine is a single Flask application that uses html templates and JQuery for the frontend and a MongoDB database. This was the stack that the application was originally developed in, and for now, we'll make do with what we've got.

### Authentication

The application uses GitLab's OAuth2 service to perform user authentication. Thus, all users must have accounts on the core GitLab virtual lab. Maybe we'll add Google OAuth2 at some point if we have users outside a classroom network.

### Running Locally

First create a python virtual environment: virtualenv venv.

Activate the virtual environment: `$source venv/bin/activate`.

Install dependencies: `pip install -r requirements.txt`.

Start a MongoDB instance locally with whatever data directory you want to use. Typically, `$mongod --dbpath ./data/db`

Run server: `python server.py`.

### Tests

Yeah, there's no testing on this application either. Feel free to add these and make a PR. Bad development practice, I know.



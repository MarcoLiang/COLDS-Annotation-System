from flask import make_response, jsonify
from flask_restful import Resource, reqparse

from schema.Query import Query
from schema.Dataset import Dataset
from schema.Assignment import Assignment
from schema.Annotation import Annotation

from util.userAuth import login_auth_required
import os, json

env = os.environ["APP_ENV"]
cfg = json.loads(open('config.json').read())[env]

parser = reqparse.RequestParser()
parser.add_argument('dataset', type=str)

class ExtractAPI(Resource):
    @login_auth_required
    def post(self):
	args = parser.parse_args()
        dataset_id = args['dataset']
        dataset = Dataset.objects(id=dataset_id).first()
    
        assignments = Assignment.objects(dataset=dataset_id)
        assignment_ids = [a.id for a in assignments]
        queries = Query.objects(assignment__in=assignment_ids)
        query_ids = [q.id for q in queries]

        to_write = []
        valid_query_num = 0
        for query_id in query_ids:
            annotations = Annotation.objects(query=query_id)
            judgements = {}
            for a in annotations:
                doc_num = a.document.name[:-4]
                judge_score = 1 if a.judgement == "relevant" else 0
                if doc_num in judgements:
                    judgements[doc_num].append(judge_score)
                else:
                    judgements[doc_num] = [judge_score]
            
            overall_judgements = {}
            is_valid = False
            for doc_num in judgements:
                judgem = sum(judgements[doc_num]) / len(judgements[doc_num])
                if judgem > 0:
                    overall_judgements[doc_num] = judgem
                    is_valid = True

            if is_valid:
                entries = {"docs": [], "query_id": query_id}
                for doc_num in overall_judgements:
                    entry = (valid_query_num, doc_num, overall_judgements[doc_num])
                    entries["docs"].append(entry)
                to_write.append(entries)
                valid_query_num += 1

    
        path = cfg["dataset_base_path"] + str(dataset.owner.gitlab_id) + \
                "/" + dataset.name + "/"
        qrels_filename = dataset.name + "-qrels.txt"
        queries_filename = dataset.name + "-queries.txt"

        for entries in to_write:
            query_id = entries["query_id"]
            with open(path + queries_filename, 'a') as f:
                query = Query.objects(id=query_id).first()
                f.write(query.content + "\n")
                f.close()

            with open(path + qrels_filename, 'a') as f:
                for entry in entries["docs"]:
                    qnum, doc_num, judgement = entry
                    f.write(str(qnum) + " " + str(doc_num) + " " + str(judgement) + "\n")
                f.close()

        ### Need to add implementation to copy dataset to permanent data directory,
        ### out of annotatable_datasets subdirectory

        response = {
            "status": "success",
            "queries_filepath": path + queries_filename,
            "qrels_filepath": path + qrels_filename
        }

        return make_response(jsonify(response))




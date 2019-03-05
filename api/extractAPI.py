from flask import make_response, jsonify
from flask_restful import Resource, reqparse

from schema.Query import Query
from schema.Dataset import Dataset
from schema.Assignment import Assignment
from schema.Annotation import Annotation

from util.userAuth import login_auth_required
import os, json, shutil
import pytoml as toml

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
        queries = Query.objects(assignment__in=assignment_ids, submitted=True)
        query_ids = [q.id for q in queries]

        metadata_filepath = cfg["anno_dataset_base_path"] + str(dataset.owner.gitlab_id) + "/" + dataset.name + "/metadata.data"
        doc_ids = self._get_doc_ids(metadata_filepath)

        to_write = []
        valid_query_num = 0
        for query_id in query_ids:
            annotations = Annotation.objects(query=query_id)
            if len(annotations) < 40:
                continue

            judgements = {}
            for a in annotations:
                doc_id = doc_ids[a.document.name]
                judge_score = 1 if a.judgement == "relevant" else 0
                if doc_id in judgements:
                    judgements[doc_id].append(judge_score)
                else:
                    judgements[doc_id] = [judge_score]
            
            overall_judgements = {}
            is_valid = False
            for doc_id in judgements:
                judgem = int(round(float(sum(judgements[doc_id])) / len(judgements[doc_id])))
                if judgem > 0:
                    overall_judgements[doc_id] = judgem
                    is_valid = True

            if is_valid:
                entries = {"docs": [], "query_id": query_id}
                for doc_id in overall_judgements:
                    entry = (valid_query_num, doc_id, overall_judgements[doc_id])
                    entries["docs"].append(entry)
                to_write.append(entries)
                valid_query_num += 1

    
        old_dataset_path = cfg["anno_dataset_base_path"] + str(dataset.owner.gitlab_id) + "/" + dataset.name
        new_dataset_path = cfg["perm_dataset_base_path"]

        self._copy_dataset(old_dataset_path, new_dataset_path + '/' + dataset.name)
        self._update_dataset_config(new_dataset_path, dataset.name)

        path = cfg["perm_dataset_base_path"] + '/' + dataset.name + "/"
        qrels_filepath = path + dataset.name + "-qrels.txt"
        queries_filepath = path + dataset.name + "-queries.txt"

        self._write_query_files(to_write, queries_filepath, qrels_filepath)

        response = {
            "status": "success",
            "queries_filepath": queries_filepath,
            "qrels_filepath": qrels_filepath
        }

        return make_response(jsonify(response))


    def _get_doc_ids(self, metadata_filepath):
        doc_ids = {}
        lines = []
        with open(metadata_filepath, 'r') as f:
            lines = f.readlines()
            f.close()

        for i in range(len(lines)):
            doc_name = lines[i].split(" ")[0]
            doc_ids[doc_name] = i

        return doc_ids


    def _write_query_files(self, to_write, queries_filepath, qrels_filepath):
        if os.path.isfile(queries_filepath):
            os.remove(queries_filepath)

        if os.path.isfile(qrels_filepath):
            os.remove(qrels_filepath)

        for entries in to_write:
            query_id = entries["query_id"]
            with open(queries_filepath, 'a') as f:
                query = Query.objects(id=query_id).first()
                f.write(query.content + "\n")
                f.close()

            with open(qrels_filepath, 'a') as f:
                for entry in entries["docs"]:
                    qnum, doc_id, judgement = entry
                    f.write(str(qnum) + " " + str(doc_id) + " " + str(judgement) + "\n")
                f.close()

    
    def _copy_dataset(self, old_dataset_path, new_dataset_path):
        if os.path.isdir(new_dataset_path):
            print("Dataset already copied")
        else:
            shutil.copytree(old_dataset_path, new_dataset_path)


    def _update_dataset_config(self, ds_path, dataset_name):
        cfg = ds_path + '/' + dataset_name + '/config.toml'
        obj = dict()
        obj['prefix'] = ds_path
        obj['stop-words'] = ds_path + '/stopwords.txt'
        obj['dataset'] = dataset_name
        obj['corpus'] = "file.toml"
        obj['index'] = ds_path + '/idx/' + dataset_name + "-idx"
        obj['query-judgements'] = ds_path + '/' + dataset_name + '/' + dataset_name + '-qrels.txt'
        obj['analyzers'] = [dict()]
        analyzer = obj['analyzers'][0]
        analyzer['ngram'] = 1
        analyzer['method'] = "ngram-word"
        analyzer['filter'] = "default-unigram-chain"

        obj['query-runner'] = dict()
        obj['query-runner']['query-path'] = ds_path + '/' + dataset_name + '/' + dataset_name + '-queries.txt'
        obj['query-runner']['query-id-start'] = 0
        obj['query-runner']['timeout'] = 120

        with open(cfg, 'w+') as f:
            toml.dump(f, obj)
            f.close()

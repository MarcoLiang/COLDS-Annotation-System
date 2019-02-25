from unittest import TestCase
from search.searcher import Searcher
import pytoml as toml
import os, json
import shutil

env = os.environ["APP_ENV"]
cfg = json.loads(open('config.json').read())[env]

class TestSearcher(TestCase):

    def setUp(self):
        self.path = cfg["anno_dataset_base_path"] + str(1)
        self.ds_name = "testdataset"
        self.searcher = Searcher(ds_name=self.ds_name, path=self.path)

    def tearDown(self):
        os.remove(self.path+"/"+self.ds_name+"-config.toml")
        shutil.rmtree(self.path+"/"+self.ds_name+"-idx")
        self.path = ""
        self.ds_name = ""

    def test_search(self):
        query = "experimental investigation of the aerodynamics of a wing in a slipstream"
        ranker_name = "OkapiBM25"
        self.searcher.search(query, ranker_name)

    def test_generate_config(self):
        cfg = Searcher.generate_config(self.ds_name, self.path)
        with open(cfg, 'rb') as fin:
            obj2 = toml.load(fin)
        obj1 = dict()
        obj1['prefix'] = "."
        obj1['dataset'] = self.ds_name
        obj1['corpus'] = "file.toml"
        obj1['index'] = self.ds_name + "-idx"
        obj1['analyzers'] = [dict()]
        analyzer = obj1['analyzers'][0]
        analyzer['ngram'] = 1
        analyzer['method'] = "ngram-word"
        analyzer['filter'] = [{'type': "icu-tokenizer"}, {'type': "lowercase"}]
        self.assertDictEqual(obj1, obj2, "Config generation error")

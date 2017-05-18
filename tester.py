import glob
import os
from urllib.parse import quote_plus

import pandas as pd
import requests

import validators
from utils import pd_to_table


class SPARQLTester:
    def __init__(self, fps_dir=None):
        self.fps = []  # file paths to sparql queries we will test
        if fps_dir is None:
            self.fps = glob.glob("*.sparql")
        else:
            self.fps = glob.glob(fps_dir + "/*.sparql")

        self.tests = []

    def run(self):
        for fp in self.fps:
            test = SPARQLTest(fp)
            test.test()
            self.tests.append(test)

    def make_result_table(self):
        r = []
        for test in self.tests:
            rr = {'Query Name': test.file_name,
                  'Query Description': test.header,
                  'Validator': test.validator_class.__name__,
                  'Validator Description': test.validator.description,
                  'Test Status': "Pass" if test.validator.success else "Fail",
                  #'Query Result': test.result,
                  'Result Message': test.validator.result_message,
                  'URL': test.create_url()}
            r.append(rr)
        df = pd.DataFrame(r)
        return df

    def make_wikimedia_table(self):
        df = self.make_result_table()
        df.URL = df.URL.apply(lambda x: "[{} Run]".format(x))
        return pd_to_table(df)




def execute_sparql_query(query, prefix=None, endpoint='https://query.wikidata.org/sparql',
                         user_agent='wikidatasparqlexamples: https://github.com/SuLab/wikidatasparqlexamples'):
    wd_standard_prefix = '''
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        PREFIX wikibase: <http://wikiba.se/ontology#>
        PREFIX p: <http://www.wikidata.org/prop/>
        PREFIX v: <http://www.wikidata.org/prop/statement/>
        PREFIX q: <http://www.wikidata.org/prop/qualifier/>
        PREFIX ps: <http://www.wikidata.org/prop/statement/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    '''
    if not prefix:
        prefix = wd_standard_prefix
    params = {'query': prefix + '\n' + query,
              'format': 'json'}
    headers = {'Accept': 'application/sparql-results+json',
               'User-Agent': user_agent}
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


class SPARQLTest:

    def __init__(self, sparql_file_path):
        self.sparql_file_path = sparql_file_path
        self.file_name = os.path.basename(self.sparql_file_path)
        self.s = ''
        self.result = {}
        self.validator_class = None

        with open(self.sparql_file_path) as f:
            self.s = f.read()
        self.params = SPARQLTest.parse_header(self.s)
        self.comment = self.params['_comment']
        self.header = self.get_header(self.s)
        if 'validator' in self.params:
            if hasattr(validators, self.params['validator']):
                self.validator_class = getattr(validators, self.params['validator'])
            else:
                raise ValueError("validator '{}' not found".format(self.params['validator']))

    def create_url(self):
        url = "https://query.wikidata.org/#"
        url += quote_plus(self.s)
        url = url.replace("+", "%20")
        return url

    def test(self):
        print("running: {}".format(self.file_name))
        if not self.validator_class:
            print("{}: no validator specified".format(self.file_name))
            self.validator_class = validators.NoValidator

        result = execute_sparql_query(self.s)
        assert 'results' in result and 'bindings' in result['results']
        self.result = result['results']['bindings']
        self.validator = self.validator_class()
        self.validator.validate(self.result)

    def dummy_test(self):
        if not self.validator_class:
            print("{}: no validator specified".format(self.file_name))
            self.validator_class = validators.NoValidator
        result = {'results': {'bindings':[{'a': 2, 'b':3},{'a': 2, 'b':3}]}}
        assert 'results' in result and 'bindings' in result['results']
        self.result = result['results']['bindings']
        self.validator = self.validator_class()
        self.validator.validate(self.result)

    def print_results(self):
        s = """
Query: {}
Validator: {} ({})
PASS?: {}
-----------
SPARQL: {}
-----------
Result: {}
        """.format(self.file_name, self.validator_class.__name__,
                   self.validator.description, self.validator.success, self.s, self.result)
        print(s)

    def get_results(self):
        df = pd.DataFrame(self.result)
        return df

    @staticmethod
    def get_header(s):
        header = [line.replace("#", "") for line in s.split("\n") if line.startswith("#") and not line.startswith("##")]
        return ' '.join(header)

    @staticmethod
    def parse_header(s):
        header = [line for line in s.split("\n") if line.startswith("##")]
        params = {'_comment': "\n".join(header)}
        for line in header:
            if ":" in line:
                key = line.split(":",1)[0].replace("##", "").strip()
                params[key] = line.split(":", 1)[1].strip()
        return params

if __name__ == '__main__':
    t = SPARQLTester("maintenance")
    t.run()
    print(t.make_wikimedia_table())
import time

import gensim
import pandas as pd
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import numpy as np
import utils

# ********************** wordnet

# DO NOT CHANGE THE CLASS NAME
class SearchEngine:

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation, but you must have a parser and an indexer.
    def __init__(self, config=None):
        self._config = config
        self._parser = Parse()
        self._indexer = Indexer(config)
        self._model = None

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def build_index_from_parquet(self, fn):
        """
        Reads parquet file and passes it to the parser, then indexer.
        Input:
            fn - path to parquet file
        Output:
            No output, just modifies the internal _indexer object.
        """
        df = pd.read_parquet(fn, engine="pyarrow")
        documents_list = df.values.tolist()
        # Iterate over every document in the file
        number_of_documents = 0
        for idx, document in enumerate(documents_list):
            # parse the document
            parsed_document = self._parser.parse_doc(document)
            if parsed_document == {}:  # RT
                continue
            number_of_documents += 1
            # index the document data
            self._indexer.add_new_doc(parsed_document)
        self._indexer.inverted_idx = {key: val for key, val in self._indexer.inverted_idx.items() if val != 1}
        self._indexer.postingDict = {key: val for key, val in self._indexer.postingDict.items() if len(val) != 1}
        # print('Finished parsing and indexing.')
        # self._indexer.save_index('idx_bench')

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        self._indexer.load_index(fn)

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_precomputed_model(self, model_dir=None):
        """
        Loads a pre-computed model (or models) so we can answer queries.
        This is where you would load models like word2vec, LSI, LDA, etc. and 
        assign to self._model, which is passed on to the searcher at query time.
        """
        pass

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results.
        Input:
            query - string.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        searcher = Searcher(self._parser, self._indexer, model=self._model)
        return searcher.wordnet_search(query)

def read_queries(queries):
    # with open(queries) as f:
    with open(queries, encoding="utf8") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    return content

def main():
    # print("start: ", time.asctime(time.localtime(time.time())))
    config = ConfigClass()
    Engine = SearchEngine(config)
    # print("start: ", time.asctime(time.localtime(time.time())))
    corpus_path = "C:\\Users\\ASUS\\Desktop\\data_part_c\\data\\benchmark_data_train.snappy.parquet"
    # corpus_path = "C:\\Users\\ASUS\\Desktop\\Data\\Data\\date=07-19-2020\\covid19_07-19.snappy.parquet"
    # Engine.build_index_from_parquet( corpus_path)
    # Engine._indexer.save_index("inverted_idx")
    # print("finish: ", time.asctime(time.localtime(time.time())))

    Engine.load_index("inverted_idx")
    Engine.load_precomputed_model()
    queries = read_queries("full_queries2.txt")
    df = pd.read_parquet(corpus_path, engine="pyarrow")
    documents_list = df.values.tolist()
    i = 0
    for query in queries:
        n_relevant, ranked_doc_ids = Engine.search(query)
        for doc_tuple in ranked_doc_ids:
            for doc in documents_list:
                if doc[0] == doc_tuple[0]:
                    i += 1
                    print('tweet id: {}, similarity: {}'.format(doc_tuple[0], doc_tuple[1]))
                    print(doc[0], ":", doc[2])


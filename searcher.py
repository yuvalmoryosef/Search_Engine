from ranker import Ranker
import utils
from nltk.corpus import wordnet
import nltk


# DO NOT MODIFY CLASS NAME
class Searcher:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit. The model 
    # parameter allows you to pass in a precomputed model that is already in 
    # memory for the searcher to use such as LSI, LDA, Word2vec models. 
    # MAKE SURE YOU DON'T LOAD A MODEL INTO MEMORY HERE AS THIS IS RUN AT QUERY TIME.
    def __init__(self, parser, indexer, model=None):
        self._parser = parser
        self._indexer = indexer
        self._ranker = Ranker()
        self._model = model

    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def search(self, query, k=None):
        """ 
        Executes a query over an existing index and returns the number of 
        relevant docs and an ordered list of search results (tweet ids).
        Input:
            query - string.
            k - number of top results to return, default to everything.
        Output:
            A tuple containing the number of relevant search results, and 
            a list of tweet_ids where the first element is the most relavant 
            and the last is the least relevant result.
        """
        # query_as_list = self._parser.parse_sentence(query)
        query_as_list = self._parser.parse_query(query)

        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = self._ranker.rank_relevant_docs(self._indexer.documents_dict, self._model, relevant_docs, query_as_list, k)
        # print(n_relevant, ranked_doc_ids)
        return n_relevant, ranked_doc_ids

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _relevant_docs_from_posting(self, query_as_list):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_as_list: parsed query tokens
        :return: dictionary of relevant documents mapping doc_id to document frequency.
        """
        relevant_docs = {}
        for term in query_as_list:
            posting_list = self._indexer.get_term_posting_list(term)
            for doc_id, tf in posting_list:
                df = relevant_docs.get(doc_id, 0)
                relevant_docs[doc_id] = df + 1

        min_len = min(2000, len(relevant_docs))
        relevant_docs_sorted = dict(sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)[:min_len])
        return relevant_docs_sorted


    def basic_search(self, query, k=None):
        query_as_list = self._parser.parse_query(query)

        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = self._ranker.basic_rank_relevant_docs(relevant_docs, k)
        return n_relevant, ranked_doc_ids


    def wordnet_search(self, query, k=None):
        # nltk.download('wordnet')
        query_as_list = self._parser.parse_query(query)
        query_tmp = list(query_as_list)
        for term in query_tmp:
            synonyms = wordnet.synsets(term.lower())
            for synonym in synonyms:
                extra_term = synonym.lemmas()[0].name()
                if extra_term != term.lower():
                    query_as_list.append(extra_term)
                    break

        relevant_docs = self._relevant_docs_from_posting(query_as_list)
        n_relevant = len(relevant_docs)
        ranked_doc_ids = self._ranker.basic_rank_relevant_docs(relevant_docs, k)
        return n_relevant, ranked_doc_ids

    # def best_search(self, query, k=None):
    #     query_as_list = self._parser.parse_query(query)
    #     query_tmp = list(query_as_list)
    #     for term in query_tmp:
    #         synonyms = wordnet.synsets(term.lower())
    #         for synonym in synonyms:
    #             extra_term = synonym.lemmas()[0].name()
    #             if extra_term != term.lower():
    #                 query_as_list.append(extra_term)
    #                 break
    #
    #     relevant_docs = self._relevant_docs_from_posting(query_as_list)
    #     n_relevant = len(relevant_docs)
    #     ranked_doc_ids = self._ranker.rank_relevant_docs(self._indexer.documents_dict, self._model, relevant_docs, query_as_list, k)
    #     return n_relevant, ranked_doc_ids
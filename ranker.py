from collections import defaultdict
import time

from gensim.scripts.glove2word2vec import glove2word2vec
import numpy as np
# you can change whatever you want in this module, just make sure it doesn't
# break the searcher module
class Ranker:
    def __init__(self):
        pass

    def rank_relevant_docs(self, docs_dictionary, word2vec, relevant_docs, query, k):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param docs_dictionary:
        :param word2vec:
        :param query:
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        # ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        # if k is not None:
        #     ranked_results = ranked_results[:k]
        # return [d[0] for d in ranked_results]
        # print("start similarity At: ", time.asctime(time.localtime(time.time())))

        similarity_dictionary = defaultdict(float)
        query_vector = self.get_doc_vector(query, word2vec)
        if len(query_vector) == 0:
            return self.basic_rank_relevant_docs(relevant_docs, k)

        for tweet_id in relevant_docs:
            doc_vector = self.get_doc_vector(docs_dictionary[tweet_id][0][2], word2vec)
            try:
                sim = np.dot(doc_vector, query_vector)/((np.linalg.norm(doc_vector) * np.linalg.norm(query_vector)))
            except:
                continue

            similarity_dictionary[tweet_id] = sim

        # print("finish similarity At: ", time.asctime(time.localtime(time.time())))
        # return sorted(similarity_dictionary.items(), key=lambda x: x[1], reverse=True)[:k]
        return sorted(similarity_dictionary.keys(), key=lambda x: x[1], reverse=True)[:k]

    def get_doc_vector(self, query, word2vec):
        doc_vec = 0
        counter = 0
        avg_vec = []
        for term in query:
            if term in word2vec.wv.vocab:
                doc_vec += word2vec[str(term)]
                counter += 1
            if counter > 0:
                avg_vec = doc_vec / counter
        return avg_vec


    def basic_rank_relevant_docs(self, relevant_docs, k):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        ranked_results = sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)
        if k is not None:
            ranked_results = ranked_results[:k]
        return [d[0] for d in ranked_results]

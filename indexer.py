# DO NOT MODIFY CLASS NAME
import pickle
from collections import defaultdict
import utils

class Indexer:
    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def __init__(self, config):
        self.inverted_idx = defaultdict(int)
        self.postingDict = defaultdict(list)  # value = [(tweet_id, count_in_doc),...,(id, count)]
        self.named_entity_idx = defaultdict(list)
        self.config = config
        self.documents_dict = defaultdict(list)
        self.extra_stop_words = ['rt', 'www', 'http', 'https', 'tco', 'didnt', 'dont', 'twitter.com', '-', '|']


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            if term in self.extra_stop_words or term.lower() in self.extra_stop_words:
                continue
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    if term[0].isupper():
                        if term.lower() in self .inverted_idx.keys():  # this is upper and there was lower before -> insert as lower
                            new_term = term.lower()
                            self.inverted_idx[new_term] += 1
                            self.postingDict[new_term].append((document.tweet_id, document_dictionary[term]))
                        else:   # this is upper and there wad noting before -> insert as upper
                            self.inverted_idx[term] = 1
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

                    elif term[0].islower(): # this is lower and there wad upper before -> insert as lower and move what was at upper
                        if term.upper() in self.inverted_idx.keys():
                            self.inverted_idx[term] = self.inverted_idx[term.upper()] + 1
                            self.postingDict[term] = self.postingDict[term.upper()]
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term]))
                            # del self.inverted_idx[term.upper()]
                            self.inverted_idx.pop(term.upper())
                            del self.postingDict[term.upper()]

                        elif term.capitalize() in self.inverted_idx.keys():
                            self.inverted_idx[term] = self.inverted_idx[term.capitalize()] + 1
                            self.postingDict[term] = self.postingDict[term.capitalize()]
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term]))
                            del self.inverted_idx[term.capitalize()]
                            del self.postingDict[term.capitalize()]

                        else:  # this is lower and there wad noting before -> insert as lower
                            self.inverted_idx[term] = 1
                            self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

                    else:
                        self.inverted_idx[term] = 1
                        self.postingDict[term].append((document.tweet_id, document_dictionary[term]))
                else:  # term was in before in the same way
                    self.inverted_idx[term] += 1
                    self.postingDict[term].append((document.tweet_id, document_dictionary[term]))
                    # TODO- save  details about doc
                # self.inverted_idx = {key: val for key, val in self.inverted_idx.items() if val != 0}

            except:
                print('problem with the following key {}'.format(term[0]))
        self.add_named_entity(document)
        self.documents_dict[document.tweet_id].append((document.amount_of_unique_words, document.max_tf, document.term_doc_dictionary, document.most_frequent_term))

    def add_named_entity(self, document):
        document_named_entity = document.named_entity
        try:

            if document_named_entity is not None and len(document_named_entity) > 0:
                for name in document_named_entity.keys():
                    if name in self.extra_stop_words or name.lower() in self.extra_stop_words:
                        continue
                    if name in self.named_entity_idx.keys():  # recognize as named_entity before
                        if name or name.lower() not in self.inverted_idx.keys():
                            add_count = len(self.named_entity_idx[name])+1

                            self.inverted_idx[name] = add_count
                            self.postingDict[name].append((document.tweet_id, document_named_entity[name]))
                            self.postingDict[name].extend(self.named_entity_idx[name])

                        else:
                            self.inverted_idx[name] += 1
                            self.postingDict[name].append((document.tweet_id, document_named_entity[name]))
                        # if len(self.named_entity_idx[name]) > 0:
                        #     self.postingDict[name].extend(self.named_entity_idx[name])
                        #     del self.named_entity_idx[name]


                    else: # new possible entity
                        self.named_entity_idx[name].append((document.tweet_id, document_named_entity[name]))
        except:
            print('problem with the following key {}', document_named_entity)


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def load_index(self, fn):
        """
        Loads a pre-computed index (or indices) so we can answer queries.
        Input:
            fn - file name of pickled index.
        """
        # raise NotImplementedError
        if fn.find('.pkl') != -1:
            with open(fn, 'rb') as f:
                indexer = pickle.load(f)
        else:
            indexer = utils.load_obj(fn)
        self.inverted_idx = indexer[0]
        self.postingDict = indexer[1]
        self.documents_dict = indexer[2]
        return indexer


    # DO NOT MODIFY THIS SIGNATURE
    # You can change the internal implementation as you see fit.
    def save_index(self, fn):
        """
        Saves a pre-computed index (or indices) so we can save our work.
        Input:
              fn - file name of pickled index.
        """
        # raise NotImplementedError
        indexer = (self.inverted_idx, self.postingDict, self.documents_dict)
        utils.save_obj(indexer, fn)

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def _is_term_exist(self, term):
        """
        Checks if a term exist in the dictionary.
        """
        return term in self.postingDict

    # feel free to change the signature and/or implementation of this function 
    # or drop altogether.
    def get_term_posting_list(self, term):
        """
        Return the posting list from the index for a term.
        """
        return self.postingDict[term] if self._is_term_exist(term) else []

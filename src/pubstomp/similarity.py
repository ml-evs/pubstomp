""" This module provides an abstract class for performing
semantic/text-based similarity between two pieces of text
e.g. arXiv abstracts.

"""

class Similarity:
    def __init__(self, document_a, document_b):
        """ Load text samples and any other required data into instance.

        Parameters:
            document_a (Document): the first entry to compare.
            document_b (Document): the second entry to compare.

        Keyword arguments:
            model_type (str): the string name of the desired model, any of
                'glove', 'spacy' or 'liam'.
            pretrained_data: any pretrained data required for the model.

        """
        self.document_a = document_a
        self.document_b = document_b

        self.text_a = self.document_a.abstract
        self.text_b = self.document_b.abstract

        self.set_pretrained_data()

        self._similarity = None
        self.get_similarity()

    @property
    def similarity(self):
        if self._similarity is None:
            self._similarity = self.get_similarity()
        return self._similarity

    def set_pretrained_data(self):
        raise NotImplementedError('Calling Base class set_pretrained_data!')

    def get_similarity(self, a_words, b_words):
        raise NotImplementedError('Calling Base class get_similarity!')

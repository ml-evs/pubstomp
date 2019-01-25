""" This module provides an abstract class for performing
semantic/text-based similarity between pieces of text e.g. arXiv
abstracts.

"""


class SimilarityEngine:
    """ SimilarityEngine subclasses should take a list of Document
    types, construct/load any models required for embedding in its
    __init__, and prepare to accept pairs of Document types in the
    get_similarity method. Should the subclass need to do any
    expensive parsing of the Document type, it should implement the
    parse_document staticmethod, which will store this parsed
    representation under Document._parsed.

    Parameters:
        documents (:obj:`list` of :obj:`document.Document`): list
            of documents required to construct the engine.

    Attributes:
        self.data (dict): a dictionary containing, with the subclass
            developer's discretion, the data used to train the model
            and the model itself, for some broad definition of model.

    """
    @staticmethod
    def parse_document(document):
        """ If any further document parsing is required by the
        subclass, do it here, and return the parsed document
        to be stored under the Document.parsed property. If this
        class is not implemented by the subclass, return the
        original document.

        Parameters:
            document (document.Document): the document to parse.

        """
        return document

    def get_similarity(self, document_a, document_b):
        """ Calculate similarity between the two documents according to
        the model embedded in the subclass.

        Parameters:
            document_a (document.Document): first document to compare.
            document_b (document.Document): second document to compare.

        Returns:
            float: result of dot product in [0, 1].

        """
        raise NotImplementedError('Calling Base class get_similarity!')

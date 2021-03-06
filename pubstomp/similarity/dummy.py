import random
from pubstomp.similarity import SimilarityEngine
from pubstomp.document import Document

class DummySimilarityEngine(SimilarityEngine):
    def __init__(self, documents):
        for doc in documents:
            assert isinstance(doc, Document)
        print('Checked document list, all documents')

    @staticmethod
    def parse_document(document):
        return 'totally unique string'

    def get_similarity(self, document_a, document_b):
        # print(document_a.parsed(self), document_b.parsed(self))
        return random.random()

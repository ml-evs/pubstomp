""" This module iteratively creates a network of papers with edges
based on their pair-wise similarities, in some really fun and cool
way.

"""

import networkx
import pymongo
import copy
from document import Document
from spacy_similarity import SpacySimilarity

def create_sampled_network(num_samples=10):
    """ Iterate over mongo cursor and create network on the fly.

    """
    cursor = list(pymongo.MongoClient(serverSelectionTimeoutMS=1000).pubstomp.arXiv_v1.aggregate([{'$sample': {'size': num_samples}}]))
    graph = networkx.Graph()
    for ind, doc in enumerate(cursor):
        doc = Document(doc)
        graph.add_node(ind, arxiv_id=doc.arxiv_id)
        for jnd, _doc in enumerate(cursor):
            _doc = Document(_doc)
            if ind == jnd:
                continue
            graph.add_node(jnd, arxiv_id=_doc.arxiv_id)
            result = SpacySimilarity(doc, _doc).similarity
            print(doc.arxiv_id, _doc.arxiv_id, result)
            graph.add_edge(ind, jnd, similarity=result)

    print(graph)


if __name__ == '__main__':
    create_sampled_network(num_samples=10)

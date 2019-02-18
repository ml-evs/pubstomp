#!/usr/bin/env python
""" This module implements the main pubstomp routine for comparing
arXiv papers with various methods/representations.

"""

import pymongo as pm
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pubstomp.document import Document
from pubstomp.similarity import GloveSimilarityEngine, DummySimilarityEngine
import argparse


def pub_stomp(num_train_documents, num_test_documents, engine_type='test'):
    """ Pull two samples of documents from the mongo and construct the
    similarity model on the training set of num_train_documents, then
    calculate pairwise similarities on the test set of
    num_test_documents.

    Note:
        Assumes Mongo is accessible on localhost:27017.

    Parameters:
        num_train_documents (int): size of random training set.
        num_test_documents (int): size of random test set.

    Keyword arguments:
        engine_type (str): the name of the similarity engine to use,
            options are 'glove', 'spacy' or 'test'.

    """
    db = pm.MongoClient().pubstomp.arXiv_v0

    training_sample = list(db.aggregate([{'$sample': {'size': num_train_documents}}]))
    training_set = [Document(doc) for doc in training_sample]

    test_sample = db.aggregate([{'$sample': {'size': num_test_documents}}])
    test_set = [Document(doc) for doc in test_sample]

    if engine_type == 'test':
        sim_engine = DummySimilarityEngine(training_set)
    elif engine_type == 'glove':
        sim_engine = GloveSimilarityEngine(training_set)
    else:
        raise NotImplementedError

    heatmap = np.zeros((num_test_documents, num_test_documents))
    asymmetry_diff = []
    for ind, doc_a in enumerate(test_set):
        for jnd, doc_b in enumerate(test_set):
            if ind > jnd:
                continue
            similarity = sim_engine.get_similarity(doc_a, doc_b)
            heatmap[ind, jnd] = similarity
            similarity = sim_engine.get_similarity(doc_b, doc_a)
            heatmap[jnd, ind] = similarity
            asymmetry_diff.append(heatmap[ind, jnd] - heatmap[jnd, ind])

    np.savetxt('heatmap.dat', heatmap)
    np.savetxt('asymmetry_diff.dat', asymmetry_diff)
    sns.heatmap(heatmap)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stomps them pubs.')
    parser.add_argument('--num_train', nargs='?', help='num_train help', const=100, default=100, type=int)
    parser.add_argument('--num_test', nargs='?', help='num_test help', const=100, default=100, type=int)
    parser.add_argument('--engine', nargs='?', help='engine help', const='test', default='test')
    args = parser.parse_args()
    
    pub_stomp(args.num_train, args.num_test, args.engine)

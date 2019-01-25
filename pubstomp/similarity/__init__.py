""" Similarity methods. """

__all__ = ['SimilarityEngine', 'GloveSimilarityEngine', 'DummySimilarityEngine', 'SpacySimilarityEngine']
__author__ = ['Matthew Evans', 'Will Grant', 'Liam Pattinson', 'Mark Johnson']
__maintainer__ = ['Matthew Evans', 'Will Grant', 'Liam Pattinson', 'Mark Johnson']

from pubstomp.similarity.similarity import SimilarityEngine
from pubstomp.similarity.glove import GloveSimilarityEngine
from pubstomp.similarity.dummy import DummySimilarityEngine
from pubstomp.similarity.spacy import SpacySimilarityEngine

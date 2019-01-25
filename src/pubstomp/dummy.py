import random

class DummyEngine(SimilarityEngine):
  def __init__(self, documents):
    print('Yeah, I got nothing useful for you here.')
  
  @staticmethod
  def parse_document(document):
    print('Ha. Ha. Ha. You really think I\'m gonna parse that for you?')
  
  def get_similarity(self, document_a, document_b):
    print('Okay, I\'ll look at \'em.')
    _ = document_a.parsed(self)
    _ = document_b.parsed(self)
    print('Nope. Pile of stink. Have this garbage instead.')
    return random.random()

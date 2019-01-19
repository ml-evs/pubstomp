import re
import collections
from functools import reduce

import numpy as np
import pymongo as db

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

stemmer = PorterStemmer()

# ======================

def get_uniques(L):
    d = collections.defaultdict(int)
    for x in L: d[x] += 1
    return [x for x in L if d[x] == 1]

def remove_intersection(L1,L2):
    return [l for l in L2 if l not in L1] + [l for l in L1 if l not in L2]

def remove_dupes(L):
    return list(set(L))

def remove_non_words(L):
    return [l for l in L if not re.search("""[0-9,;_:'"`~=()<>\\\|\+\[\]\{\}\.\$\*\^]""",l)]

# ======================

db_client = db.MongoClient()
papers = db_client.pubstomp.arXiv_v1.find()

#M = papers.count() # number of examples
M = 100

abstracts = []

for i,paper in enumerate(papers):
    abstracts.append(max(paper['description'],key=len))
    if i == M:
        break

# Get list of stemmed words
words = reduce((lambda x,y: x+y),abstracts)
words = re.sub('\s+', ' ', words).strip() # replace all whitespaces with a single space
wordlist = word_tokenize(words)
wordlist = [stemmer.stem(w) for w in wordlist]
# Remove any unique words (those that only appear once across all abstracts)
unique_wordlist = get_uniques(wordlist)
wordlist = remove_intersection(wordlist,unique_wordlist)
# Remove any words that contain dollar signs, backslashes, numerals, or most punctuation (not -, anything else though)
wordlist = remove_non_words(wordlist)
# Remove duplicates
wordlist = remove_dupes(wordlist)

print(wordlist)
print(len(wordlist))

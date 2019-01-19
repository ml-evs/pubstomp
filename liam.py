import re
import collections
from functools import reduce

import numpy as np
import pymongo as db

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

# ======================
# Misc helper functions

def get_uniques(L):
    """
    Given list L of words, return list of words that only appear once in the list
    """
    d = collections.defaultdict(int)
    for x in L: d[x] += 1
    return [x for x in L if d[x] == 1]

def remove_intersection(L1,L2):
    """
    Given two lists L1 and L2 of words, return list of words that only appear in one of L1 or L2
    """
    return [l for l in L2 if l not in L1] + [l for l in L1 if l not in L2]

def remove_dupes(L):
    """
    Given list L of words, return set of unique words
    """
    return list(set(L))

def remove_non_words(L):
    """
    Given list L of 'words', remove anything which looks more like punctuation, maths, etc.
    """
    return [l for l in L if not re.search("""[0-9,;_:'"`~=()<>\\\|\+\[\]\{\}\.\$\*\^]""",l)]

# ======================
# Bigger functions

def get_abstracts(M=100):
    """
    Accesses abstract database, returns list of first M abstracts.
    Abstracts are represented as a list of strings. Each list element is a single abstract.
    """
    db_client = db.MongoClient()
    papers = db_client.pubstomp.arXiv_v1.find()

    abstracts = []
    for i,paper in enumerate(papers):
        abstracts.append(max(paper['description'],key=len))
        if i == M:
            break
    return abstracts

def abstract_to_wordlist(abstract):
    """
    Converts an abstract to a list of unique and useful words contained within in
    """
    words = re.sub('\s+', ' ', abstract).strip() # replace all whitespaces with a single space
    wordlist = word_tokenize(words)
    # Stem -- remove suffixes etc. Uses simple Porter stemmer
    stemmer = PorterStemmer()
    wordlist = [stemmer.stem(w) for w in wordlist]
    # Remove any words that contain dollar signs, backslashes, numerals, etc.
    wordlist = remove_non_words(wordlist)
    # Remove any unique words (those that only appear once across all abstracts)
    unique_wordlist = get_uniques(wordlist)
    wordlist = remove_intersection(wordlist,unique_wordlist)
    # Remove duplicates
    wordlist = remove_dupes(wordlist)
    return wordlist

def get_word_space(abstracts):
    """
    Given list of abstracts (see 'get_abstracts'), returns list of words that may be used to
    classify them.
    """
    # Convert all abstracts to one long string
    words = reduce((lambda x,y: x+y),abstracts)
    wordlist = abstract_to_wordlist(words)
    # Create mapping
    return dict([[v,k] for k,v in enumerate(wordlist)])

def to_word_space(abstract,wordmap):
    """
    Converts an abstract to a vector in 'word space'
    Returns a numpy array
    """
    wordlist = abstract_to_wordlist(abstract)
    intlist  = [wordmap[w] for w in wordlist]
    return np.array([1 if i in intlist else 0 for i in range(len(wordmap))])

def get_similarities(X,y):
    """
    Takes matrix X of abstracts converted to vectors in word space
    Shape: ( num_abstracts, num_features)
    Takes vector y in word space
    Returns vector of similarities
    """
    return X@y
    

if __name__ == '__main__':
    abstracts = get_abstracts(500)
    M = len(abstracts) # Number of examples
    print("Num examples: ",M)
    wordmap = get_word_space(abstracts)
    N = len(wordmap)   # Number of features
    print("Num features: ",N)
    X = np.zeros((M,N))
    for i,abstract in enumerate(abstracts):
        X[i] = to_word_space(abstract,wordmap)
    choice = -1
    while choice < 0 or choice >= M:
        choice = int(input("Choose paper number (max" + str(M) + ")\n"))
    print("You chose:")
    print(abstracts[choice])
    print("\n==============================\n")
    similarities = get_similarities(X,X[choice])
    print(similarities)
    # Get top 10 (not counting self, which should give the maximum similarity
    top_10 = sorted(range(len(similarities)), key=lambda i: similarities[i])[-11:-1]
    top_10.reverse()
    print("Your top 10 papers:")
    print(top_10)
    print("\n==============================\n")
    for paper in top_10:
        print(abstracts[paper])
        print("\n==============================\n")



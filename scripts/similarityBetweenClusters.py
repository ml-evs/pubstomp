"""
Load the three datasets.
Get the nlp similarity between the abstracts.
"""

# import pymongo
# import json
import bson.json_util
# import numpy as np
with open("maths_short.json") as flines:
    maths = bson.json_util.loads(flines.read())
with open("materials_short.json") as flines:
    materials = bson.json_util.loads(flines.read())
with open("physics_short.json") as flines:
    physics = bson.json_util.loads(flines.read())
 
columns = ["id", "description", "label"]
data = []
for doc in maths:
    data.append([
        doc["arxiv_id"],
        max(doc['description'], key=len).replace("\n", " ").strip(),
        "maths"
     ])
for doc in materials:
    data.append([
        doc["arxiv_id"],
        max(doc['description'], key=len).replace("\n", " ").strip(),
        "materials"
     ])
for doc in physics:
    data.append([
        doc["arxiv_id"],
        max(doc['description'], key=len).replace("\n", " ").strip(),
        "physics"
     ])



import spacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

# Determine semantic similarities

nlpData = [[x, nlp(y), z] for x,y,z in data]
triangle = []
for i, row in enumerate(nlpData):
    triRow = []
    for j, row2 in enumerate(nlpData[:i]):
        print(i,j)
        triRow.append(row[1].similarity(row2[1]))
# print(doc1.text, doc2.text, similarity)
    triangle.append(triRow)

with open("tri.txt", "w") as flines:
    flines.write("\n".join(" ".join(map(str, x)) for x in triangle))
print(triangle)

square = []
for i, row in enumerate(nlpData):
    squareRow = []
    for j, row2 in enumerate(nlpData):
        # print(i,j)
        squareRow.append(row[1].similarity(row2[1]))
# print(doc1.text, doc2.text, similarity)
    square.append(squareRow)

with open("square.txt", "w") as flines:
    flines.write("\n".join(" ".join(map(str, x)) for x in square))
print(square)
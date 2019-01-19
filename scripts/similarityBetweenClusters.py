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

print(data)
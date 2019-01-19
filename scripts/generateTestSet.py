"""
generate a test set of three different subjects.

Subjects:
- Mathematics - Number Theory
- Condensed Matter - Materials Science
- Physics - Fluid Dynamics
"""
import pymongo
# import json
import bson.json_util
import numpy as np
# from bson.json_util import dumps, RELAXED_JSON_OPTIONS
client = pymongo.MongoClient()
collection = client.pubstomp.arXiv_v1


subjects = ["Mathematics - Number Theory", "Condensed Matter - Materials Science", "Physics - Fluid Dynamics"]

maths = collection.find({"subject": subjects[0]})
with open("maths_short.json", "w") as flines:
    maths = np.random.choice(list(maths), 100)
    flines.write(bson.json_util.dumps(list(maths), json_options=bson.json_util.RELAXED_JSON_OPTIONS))

materials = collection.find({"subject": subjects[1]})
with open("materials_short.json", "w") as flines:
    materials = np.random.choice(list(materials), 100)
    flines.write(bson.json_util.dumps(list(materials), json_options=bson.json_util.RELAXED_JSON_OPTIONS))

# print(materials.count())
physics = collection.find({"subject": subjects[2]})
with open("physics_short.json", "w") as flines:
    physics = np.random.choice(list(physics), 100)
    
    flines.write(bson.json_util.dumps(list(physics), json_options=bson.json_util.RELAXED_JSON_OPTIONS))

# print(physics.count())


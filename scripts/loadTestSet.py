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
with open("maths_short.json") as flines:
    maths = bson.json_util.loads(flines.read())
 
 
print(len(maths))
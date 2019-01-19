import pymongo
import json
from tqdm import tqdm
client = pymongo.MongoClient()
collection = client.pubstomp.arXiv_v1


subjectCounts = {}
errors = 0
for document in tqdm(collection.find(), total=721000):
    try:
        subjects = document["subject"]  # iterate the cursor
    except KeyError:
        errors += 1
        continue
    for subject in subjects:
        try:
            subjectCounts[subject] +=1
        except KeyError:
            subjectCounts[subject] = 1


with open("counts.json", "w") as flines:
    json.dump(subjectCounts, flines)

print(errors)  #  11 errors

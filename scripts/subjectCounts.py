import pymongo
import json
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt
client = pymongo.MongoClient()
collection = client.pubstomp.arXiv_v1


# subjectCounts = {}
# errors = 0
# for document in tqdm(collection.find(), total=721000):
#     try:
#         subjects = document["subject"]  # iterate the cursor
#     except KeyError:
#         errors += 1
#         continue
#     for subject in subjects:
#         try:
#             subjectCounts[subject] +=1
#         except KeyError:
#             subjectCounts[subject] = 1


# with open("counts.json", "w") as flines:
#     json.dump(subjectCounts, flines)

# print(errors)  #  11 errors

with open("counts.json") as flines:
    subjectCounts = json.load(flines)

subjectCounts = sorted([[x,y] for x,y in subjectCounts.items()],key=lambda x: x[1], reverse=True)[:50]

print(subjectCounts)
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(20,15))
ax = sns.barplot(x=[x[0]for x in subjectCounts], y=[x[1] for x in subjectCounts])
plt.xticks(rotation=90)
fig.subplots_adjust(bottom=0.4)
# plt.tight_layout()
ax.xaxis.label.set_size(8)
plt.savefig("subjectsHistogram.png", dpi=500)
plt.show()

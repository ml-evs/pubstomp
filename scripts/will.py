import spacy


def getSimilarity(document1, document2):
    """
    Given two documents (either the bare records or a Document class)
    return a tuple (id1, id2, simScore) indicating their semantic similarity.

    Assumes documents have the same type.
    """
    nlp = spacy.load('en_core_web_sm')

    # load the text

    # if isinstance(document1, Document):
    if False:  # FIXME this awaits a document class
        id1 = document1.arxiv_id
        text1 = document1.abstract
        id2 = document2.arxiv_id
        text2 = document2.abstract
    elif isinstance(document1, dict):
        id1 = document1["arxiv_id"]
        text1 = max(document1['description'], key=len).replace("\n", " ").strip()
        id2 = document2["arxiv_id"]
        text2 = max(document2['description'], key=len).replace("\n", " ").strip()
    
    # perform the nlp

    text1 = nlp(text1)
    text2 = nlp(text2)
    similarity = text1.similarity(text2)
    return (id1, id2, similarity)


if __name__ == "__main__":
    import bson.json_util
    with open("maths_short.json") as flines:
        maths = bson.json_util.loads(flines.read())
    with open("materials_short.json") as flines:
        materials = bson.json_util.loads(flines.read())
    with open("physics_short.json") as flines:
        physics = bson.json_util.loads(flines.read())
    
    columns = ["id", "description", "label"]
    data = []
    for doc in maths:
        data.append(doc)
        # data.append([
        #     doc["arxiv_id"],
        #     max(doc['description'], key=len).replace("\n", " ").strip(),
        #     "maths"
        # ])
    for doc in materials:
        data.append(doc)
        
        # data.append([
        #     doc["arxiv_id"],
        #     max(doc['description'], key=len).replace("\n", " ").strip(),
        #     "materials"
        # ])
    for doc in physics:
        data.append(doc)
        
        # data.append([
        #     doc["arxiv_id"],
        #     max(doc['description'], key=len).replace("\n", " ").strip(),
        #     "physics"
        # ])    

    square = []
    for i, doc in enumerate(data):
        squareRow = []
        for j, doc2 in enumerate(data):
            print(i,j)
            similarity = getSimilarity(doc, doc2)
            squareRow.append(similarity[2])
            print(squareRow)
    # print(doc1.text, doc2.text, similarity)
        square.append(squareRow)
    with open("square.txt", "w") as flines:
        flines.write("\n".join(" ".join(map(str, x)) for x in square))
    print(square)


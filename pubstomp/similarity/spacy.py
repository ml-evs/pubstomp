from pubstomp.similarity import SimilarityEngine
from pubstomp.document import Document


class SpacySimilarityEngine(SimilarityEngine):
    try:
        import spacy
        SPACY_EN_CORE_WEB_SM = spacy.load('en_core_web_sm')
    except ImportError:
        pass
    def get_similarity(self):
        """
        Given two documents (either the bare records or a Document class)
        return a tuple (id1, id2, simScore) indicating their semantic similarity.

        """
        nlp = self.pretrained_data['nlp']
        self.parsed_text_a = nlp(self.text_a)
        self.parsed_text_b = nlp(self.text_b)
        return self.parsed_text_a.similarity(self.parsed_text_b)

    def set_pretrained_data(self):
        self.pretrained_data = {'nlp': SPACY_EN_CORE_WEB_SM}


if __name__ == "__main__":
    import bson.json_util
    from bson.json_util import RELAXED_JSON_OPTIONS
    with open("../../data/maths_short.json") as flines:
        maths = bson.json_util.loads(flines.read(), json_options=RELAXED_JSON_OPTIONS)
    with open("../../data/materials_short.json") as flines:
        materials = bson.json_util.loads(flines.read())
    with open("../../data/physics_short.json") as flines:
        physics = bson.json_util.loads(flines.read())

    columns = ["id", "description", "label"]
    data = []
    for doc in maths:
        data.append(Document(doc))
        # data.append([
        #     doc["arxiv_id"],
        #     max(doc['description'], key=len).replace("\n", " ").strip(),
        #     "maths"
        # ])
    for doc in materials:
        data.append(Document(doc))

        # data.append([
        #     doc["arxiv_id"],
        #     max(doc['description'], key=len).replace("\n", " ").strip(),
        #     "materials"
        # ])
    for doc in physics:
        data.append(Document(doc))

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
            similarity = SpacySimilarityEngine(doc, doc2).similarity
            squareRow.append(similarity)
            print(squareRow)
    # print(doc1.text, doc2.text, similarity)
        square.append(squareRow)
    with open("square.txt", "w") as flines:
        flines.write("\n".join(" ".join(map(str, x)) for x in square))
    print(square)

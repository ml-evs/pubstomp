""" This module implements the Document class to store
arXiv records.

"""

import copy

class Document:
    def __init__(self, json_doc):
        self._raw_json = copy.deepcopy(json_doc)
        self._arxiv_id = None
        self._date_submitted = None
        self._abstract = None
        self._title = None
        self._parsed = None

    @property
    def parsed(self, sim_engine):
        """ Returns the parsed form of this document, as requested by
        sim_engine.

        """
        if not self._parsed:
            self._parsed = sim_engine.parse_document(self)
        return self._parsed

    @property
    def arxiv_id(self):
        try:
            if self._arxiv_id is None:
                self._arxiv_id = self._raw['arxiv_id']
        except KeyError:
            print('Paper is missing arXiv ID.')
        return self._arxiv_id

    @property
    def abstract(self):
        """ Gets longest item in `description`. """
        try:
            if self._abstract is None:
                self._abstract = max(self._raw['description'], key=len).replace("\n", " ").strip()
        except KeyError:
            print('Paper is missing abstract!')

        return self._abstract

    @property
    def title(self):
        """ Grabs the title of the paper. """
        try:
            if self._title is None:
                self._title = self._raw['title'].strip()
        except KeyError:
            print('Paper is missing title!')
        return self._title

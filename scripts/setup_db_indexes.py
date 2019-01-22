#!/usr/bin/env python
""" Simple script to reindex a collection of arXiv abstracts
based on date and arXiv_id.

"""
import pymongo
import sys


def index_collection(db_name='pubstomp'):
    """ (Re)index arXiv abstract database over header_date and arXiv_id keys. """
    try:
        collection_name = sys.argv[1]
    except IndexError:
        raise SystemExit('Missing collection name argument.')

    client = pymongo.MongoClient()
    db = client[db_name]

    if collection_name in db.list_collection_names():
        db[collection_name].crreate
        if collection_name in db.list_collection_names():
            index_keys = ['header_date', 'arxiv_id']
            for key in index_keys:
                if key not in db[collection_name].index_information():
                    print(f'Creating index over key: {key}.')
                    db[collection_name].create_index(key, unique=True)
            print(f'Re-indexing over all keys: {index_keys}.')
            db[collection_name].reindex()


if __name__ == '__main__':
    index_collection()

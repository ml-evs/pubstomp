#!/usr/bin/env python

""" Simple OAI-PMH scraper for arXiv, powered by Requests.

Links:

    https://www.openarchives.org/OAI/2.0/guidelines-harvester.htm
    https://arxiv.org/help/oa/index

"""

import datetime
import time
import logging
from xml.etree import ElementTree
import pymongo
import requests


def mongo_setup(db_name='pubstomp'):
    """ Connects to MongoDB, counts up from zero and creates a collection with the
    next highest int, n, in the name arXiV_v{n}.

    Keyword arguments:
        db_name (str): name of the MongoDB database to set up.

    """

    client = pymongo.MongoClient()
    db = client[db_name]
    found = False
    version = 0
    while not found:
        coll_name = f'arXiv_v{version}'
        if coll_name in db.list_collection_names():
            version += 1
        else:
            found = True

    logging.debug(f'Creating MongoDB collection {coll_name} inside database {db_name}.')

    return db[coll_name]


def mongo_clean(db_name='pubstomp'):
    """ Clear all collections named arXiv_v* in the given db name.

    Keyword arguments:
        db_name (str): name of the MongoDB database to set up.

    """

    client = pymongo.MongoClient()
    db = client[db_name]
    for coll_name in db.list_collection_names():
        if coll_name.startswith('arXiv_v'):
            db[coll_name].drop_indexes()
            db[coll_name].drop()
            logging.debug(f'Dropped {coll_name}.')


def parse_xml_record(xml_record):
    """ Turn an individual record branch of an XML response record into a dictionary.

    Parameters:
        xml_record (not sure?): xml record to parse.

    Returns:
        dict: containing relevant metadata fields.

    """
    record = {}
    for header in xml_record.iter(tag='{http://www.openarchives.org/OAI/2.0/}header'):
        for identifier in header.iter(tag='{http://www.openarchives.org/OAI/2.0/}identifier'):
            record['arxiv_id'] = identifier.text.split(':')[-1]
        for date in header.iter(tag='{http://www.openarchives.org/OAI/2.0/}datestamp'):
            record['header_date'] = datetime.datetime.strptime(date.text, '%Y-%m-%d')

    for metadata in xml_record.iter(tag='{http://www.openarchives.org/OAI/2.0/}metadata'):
        for meta in metadata.iter(tag='{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'):
            record['creators'] = []
            for creator in meta.iter(tag='{http://purl.org/dc/elements/1.1/}creator'):
                record['creators'].append(creator.text)

            record['dates'] = []
            for date in meta.iter(tag='{http://purl.org/dc/elements/1.1/}date'):
                record['dates'].append(datetime.datetime.strptime(date.text, '%Y-%m-%d'))

            record['subject'] = []
            for subject in meta.iter(tag='{http://purl.org/dc/elements/1.1/}subject'):
                record['subject'].append(subject.text)

            record['description'] = []
            for desc in meta.iter(tag='{http://purl.org/dc/elements/1.1/}description'):
                record['description'].append(desc.text)

    return record


def recursive_arxiv_scrape(mongo_collection, resumption_token=None, timeout=20, num_failures=0):
    """ Recursively scrape arXiv's OAI metadata endpoint into a MongoDB collection.

    Parameters:
        mongo_collection (pymongo.Collection): the MongoDB collection to scrape into.

    Keyword arguments:
        resumption_token (str): token required to restart incomplete queries.
        timeout (int): time in seconds between queries to manage flow control.
        num_failures (int): the number of failures since last successful query.

    """

    if resumption_token is None:
        base_request = 'http://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=oai_dc'
    else:
        base_request = 'http://export.arxiv.org/oai2?verb=ListRecords&resumptionToken={}'.format(resumption_token)

    logging.debug(f'Submitting request {base_request}')
    request = requests.get(base_request)
    logging.debug(f'Received response: {request.status_code}')
    # if the request failed, try again after timeout, but accumulate number of failures
    if request.status_code != 200:
        if num_failures >= 3:
            raise RuntimeError(f'Requests fell over for 3rd time in a row, with status code {request.status_code}.\n\nFull output: {request.text}')

        time.sleep(timeout)
        return recursive_arxiv_scrape(mongo_collection, resumption_token=resumption_token, num_failures=num_failures+1)

    logging.debug('Parsing XML...')
    xml_tree = ElementTree.fromstring(request.text)

    new_resumption_token = None
    for elem in xml_tree.iter(tag='{http://www.openarchives.org/OAI/2.0/}resumptionToken'):
        new_resumption_token = elem.text
        complete_list_size = int(elem.attrib['completeListSize'])

    if new_resumption_token is not None:
        logging.debug(f'Received resumptionToken {new_resumption_token}, with total query size {complete_list_size}')
    else:
        logging.debug(f'No resumptionToken received.')

    record_batch = []
    for _record in xml_tree.iter(tag='{http://www.openarchives.org/OAI/2.0/}record'):
        record = parse_xml_record(_record)
        record_batch.append(record)

    logging.debug(f'Inserting {len(record_batch)} entries.')
    mongo_collection.insert_many(record_batch)
    total_count = mongo_collection.count_documents({})
    logging.info(f'{total_count} out of {complete_list_size} inserted.')
    logging.debug(f'Sleeping for {timeout} s...')
    time.sleep(timeout)

    if new_resumption_token is not None:
        return recursive_arxiv_scrape(mongo_collection, resumption_token=new_resumption_token)

    logging.info('Scrape complete!')
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    mongo_clean()
    collection = mongo_setup()
    recursive_arxiv_scrape(collection, timeout=20)

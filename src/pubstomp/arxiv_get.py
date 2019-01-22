#!/usr/bin/env python

""" Simple OAI-PMH scraper for arXiv, powered by Requests.

Links:

    https://www.openarchives.org/OAI/2.0/guidelines-harvester.htm https://arxiv.org/help/oa/index

"""

import datetime
import time
import logging
import sys
from xml.etree import ElementTree
import pymongo
import requests


def start_scrape():
    """ Start scraping arXiv, with collection name optionally
    grabbed from sys.argv[1].

    """
    logging_setup()
    try:
        coll_name = sys.argv[1]
    except IndexError:
        coll_name = None
    collection = mongo_setup(coll_name=coll_name)
    recursive_arxiv_scrape(collection, hot_start=True,
                           timeout=10)


def logging_setup():
    """ Set up logging to file and stdout. """
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().handlers = []
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s: %(message)s'))
    logging.getLogger().addHandler(stdout_handler)

    logname = 'arxiv_get.log'
    file_handler = logging.FileHandler(logname, mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)8s: %(message)s'))
    logging.getLogger().addHandler(file_handler)


def mongo_setup(db_name='pubstomp', coll_name=None):
    """ Connects to MongoDB, counts up from zero and creates a collection with the
    next highest int, n, in the name arXiV_v{n}, unless specified by coll_name.

    Keyword arguments:
        db_name (str): name of the MongoDB database to set up.
        coll_name (str): name of the desired MongoDB collection to connect to.

    """

    client = pymongo.MongoClient()
    db = client[db_name]

    if coll_name is None:
        found = False
        version = 0
        while not found:
            coll_name = f'arXiv_v{version}'
            if coll_name in db.list_collection_names():
                version += 1
            else:
                found = True
    else:
        if coll_name in db.list_collection_names():
            msg = f'Using existing collection on {coll_name}.'
            logging.debug(msg)

    msg = f'Creating MongoDB collection {coll_name} inside database {db_name}.'
    logging.debug(msg)

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
            msg = f'Dropped {coll_name}.'
            logging.debug(msg)


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

            for title in meta.iter(tag='{http://purl.org/dc/elements/1.1/}title'):
                record['title'] = title.text

    return record


def recursive_arxiv_scrape(mongo_collection, resumption_token=None, timeout=10, num_failures=0, hot_start=False):
    """ Recursively scrape arXiv's OAI metadata endpoint into a MongoDB collection.

    Parameters:
        mongo_collection (pymongo.Collection): the MongoDB collection to scrape into.

    Keyword arguments:
        resumption_token (str): token required to restart incomplete queries.
        timeout (int): time in seconds between queries to manage flow control.
        num_failures (int): the number of failures since last successful query.
        hot_start (bool): query for documents added since last previous date existing
            in collection.

    Returns:
        int: the number of documents added.

    """

    last_date = None
    if hot_start:
        last_date = mongo_collection.find_one({}, sort=[('_id', pymongo.DESCENDING)])['header_date']
        msg = f'Found last date {last_date}'
        logging.debug(msg)

    base_request = 'http://export.arxiv.org/oai2?verb=ListRecords'
    if resumption_token is not None:
        base_request += '&resumptionToken={}'.format(resumption_token)
    else:
        if last_date is not None:
            base_request += '&from={}'.format(last_date.strftime('%Y-%m-%d'))

        base_request += '&metadataPrefix=oai_dc'

    msg = f'Submitting request {base_request}'
    logging.debug(msg)

    request = requests.get(base_request)

    msg = f'Received response: {request.status_code}'
    logging.debug(msg)

    # if the request failed, try again after timeout, but accumulate number of failures
    if request.status_code != 200:
        if num_failures >= 3:
            raise RuntimeError(f'Requests fell over for 3rd time in a row, with status code {request.status_code}.\n\nFull output: {request.text}')

        time.sleep(timeout)
        return recursive_arxiv_scrape(mongo_collection,
                                      resumption_token=resumption_token,
                                      timeout=timeout,
                                      hot_start=hot_start,
                                      num_failures=num_failures+1)

    logging.debug('Parsing XML...')
    xml_tree = ElementTree.fromstring(request.text)

    new_resumption_token = None
    for elem in xml_tree.iter(tag='{http://www.openarchives.org/OAI/2.0/}resumptionToken'):
        new_resumption_token = elem.text
        complete_list_size = int(elem.attrib['completeListSize'])

    if new_resumption_token is not None:
        msg = f'Received resumptionToken {new_resumption_token}, with total query size {complete_list_size}'
        logging.debug(msg)
    else:
        logging.debug(f'No resumptionToken received.')

    record_batch = []
    for _record in xml_tree.iter(tag='{http://www.openarchives.org/OAI/2.0/}record'):
        record = parse_xml_record(_record)
        record_batch.append(record)

    msg = 'Inserting {len(record_batch)} entries.'
    logging.debug(msg)
    mongo_collection.insert_many(record_batch)
    total_count = mongo_collection.count_documents({})

    msg = f'{total_count} out of {complete_list_size} inserted.'
    logging.info(msg)
    msg = f'Sleeping for {timeout} s...'
    logging.debug(msg)

    time.sleep(timeout)

    if new_resumption_token is not None:
        return recursive_arxiv_scrape(mongo_collection, hot_start=hot_start,
                                      resumption_token=new_resumption_token,
                                      timeout=timeout)

    logging.info('Scrape complete!')
    return total_count


if __name__ == '__main__':
    start_scrape()

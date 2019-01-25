#!/usr/bin/env python

""" Random assorted shit. """


def date_graph():
    """ Plot a cumulative graph of dates papers were added to
    the arXiv database.

    """
    import pymongo as pm
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os
    import numpy as np
    import seaborn as sns
    import json
    from collections import defaultdict

    if os.path.isfile('years.json'):
        with open('years.json', 'r') as f:
            years = json.load(f)

    else:
        db = pm.MongoClient().pubstomp.arXiv_v1
        dates = db.find({}, {'dates': 1})
        years = defaultdict(int)
        bad_count = 0
        for doc in dates:
            try:
                date_list = doc['dates']
            except KeyError:
                print(doc)
                bad_count += 1
                pass
            year = int(min(date_list).strftime('%Y'))
            years[year] += 1

    print(years)
    with open('years.json', 'w') as f:
        json.dump(years, f)

    raw_years = list(years.keys())
    raw_counts = list(years.items())

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot([int(key) for key in years], np.cumsum([years[key] for key in years]))
    ax.set_xlabel('Year of submission')
    ax.set_ylabel('Cumulative number of papers')
    ax.set_xticks([int(key) for key in years])
    plt.savefig('years.pdf')


if __name__ == '__main__':
    date_graph()

# -*- coding: utf-8 -*-
"""

@author: Marc Garnica Caparrós
# --------------------------------------------------------------------------
Reusable functions for elastic search functionalities and main queries
# --------------------------------------------------------------------------
"""

from elasticsearch import Elasticsearch
import numpy as np
import requests
import logging
import time
import json
from settings import ES_BASE_URL

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

def drop_database():
    logging.debug("ESUtils: Deleting all the content of the database")
    try:
        es.indices.delete(index='*')
    except Exception as e:
        logging.error("ESUtils: Something went wrong cleaning and dropping the database")
        logging.error(e)

def launch_local_server(delete,w=None, p=None):
    logging.debug('ESUtils: Waiting until Elastic Search is running')
    waiting = True
    while waiting:
        try:
            check = requests.get(ES_BASE_URL)
            if check.status_code == 200:
                waiting = False
            else:
                logging.debug('ESUtils: Waiting for the server to start')
                time.sleep(5)
        except Exception as e:
            logging.debug('ESUtils: Waiting for the server to start')
    logging.debug('ESUtils: Local server running correctly')
    if delete:
        drop_database()
        return 0
    elif p is None:
        return 0
    else:
        query_last_cycle = query_ts_sorted_values(p, 1)
        logging.debug("Searching for index %s and pump %s" % (w.lower(), p))
        data = es.search(index=w.lower(), body=query_last_cycle)
        print(data)
        last_cycle = get_source_value(data, 'cycle')
        return last_cycle

def get_source_value(response, param):
    try:
        return response['hits']['hits'][0]['_source'][param]
    except Exception as e:
        logging.exception('Something went wrong with the ES response access')
    return None

def get_source_vector_value(response, *params):
    try:
        prev = {}
        for p in params:
            prev[p] = []
        for s in response['hits']['hits']:
            source = s['_source']
            new = {}
            for p in params:
                prev[p].append(source[p])
        result = {}
        for p in params:
            result[p] = np.array(prev[p])
        return result
    except Exception as e:
        logging.exception('Something went wrong getting the vector value')
    return None

def query_last_cycle(pump):
    q = {
        'query' : {
            'match': {'pump_id': pump},
        },
        'sort': {'timestamp': {'order': 'desc'}},
        'size': 1
    }
    return q

def query_last_prediction(pump,size=1):
    q = {
        'query': {
            'match': {'pump_id': pump},
        },
        'sort': {'timestamp': {'order': 'desc'}},
        'size': size
    }
    return q

def query_prediction(pump, cycle):
    q = {
        'query': {
            'bool': {
                'must': [{
                    'match': {'pump_id': pump}
                }, {
                    'match': {
                        'cycle': cycle
                    }
                }]
            }
        }
    }
    return q

def query_cycle_values(pump, cycle):
    q = {
        'query' : {
            'bool': {
                'must': [{
                    'match': {'pump_id': pump}
                }, {
                    'match': {
                        'cycle': cycle
                    }
                }]
            }
        },
        'sort': {'timestamp': {'order': 'desc'}},
        'size': 128
    }
    return q

def query_ts_sorted_values(pump, size):
    q = {
        'query': {
            'match': {'pump_id': pump},
        },
        'sort': {'timestamp': {'order': 'desc'}},
        'size': size
    }
    return q

def query_aggregation_by_label(label, range_label, range):
    q = {
        'query': {
            "bool": {
                "must" : { "match" : { "pred_label" : label} },
                "filter" : {
                    "range": {
                        "timestamp" : {
                            range_label : range
                        }
                    }
                }
            }
        },
        "aggs": {
            "keywords": {
                "significant_text": {"field": "pred_label"}
            }
        },
        'size': 1

    }
    return q

def query_aggregation_by_label_and_pump(label, pump, range_label, range):
    q = {
        'query': {
            "bool": {
                "must" : [
                    {"match" : { "pred_label" : label} },
                    {"match" : { "pump_id": pump} }
                ],
                "filter" : {
                    "range": {
                        "timestamp" : {
                            range_label : range
                        }
                    }
                }
            }
        },
        "aggs": {
            "keywords": {
                "significant_text": {"field": "pred_label"}
            }
        },
        'size': 0

    }
    return q

def get_agg_value(response):
    try:
        return response['aggregations']['keywords']['doc_count']
    except Exception as e:
        logging.exception('Something went wrong with the ES response access')
    return None

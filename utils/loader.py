# -*- coding: utf-8 -*-
"""

@author: Marc Garnica Caparrós
# --------------------------------------------------------------------------
Utils file for loading information, configuration files and data
# --------------------------------------------------------------------------
"""

import logging
import logging.config
import pickle
import csv
import os
from settings import BASE_DIR, TAG_LIST

#load master data csv file
def load_master_data():
    master = csv.DictReader(open(os.path.join(BASE_DIR,'src', 'utils', 'avatars.csv'), 'rt'))
    return master

#load_pickle_card : Reading card from pickle file in the specified source path
def load_pickle_card(source):
    with open(source, 'rb') as f:
        cards = pickle.load(f)
    logging.debug('Images Read: %s' % len(cards))
    return(cards)

def check_folder(dir_path, create=True):
    if not os.path.exists(dir_path):
        if create:
            os.makedirs(dir_path)
            return True
        else:
            return False
    else:
        return True

def load_logging_info():
    check_folder('logs')
    logging.config.fileConfig('logging.ini')
    logger = logging.getLogger()
    logger.info('############### CHECKPOINT')
    logger.info('Logger initialized by ./logging.ini file')
    return logger

# save cards
def save_cards(cards, save_in):
    with open(save_in, 'wb') as f:
        pickle.dump(cards, f, pickle.HIGHEST_PROTOCOL)

# keep only highest probability from
def max_likelihood(x):
    label =  max(x, key=x.get)
    prob = x[label]
    return(label, prob)

def get_default_probs():
    result = {}
    for tag in TAG_LIST:
        result[tag] = float(0)
    result['normal'] = float(100)
    logging.debug(result)
    return result

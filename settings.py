# -*- coding: utf-8 -*-
"""

@author: Marc Garnica Caparrós
# --------------------------------------------------------------------------
Main settings, variables and configurations for the all the modules of the project
# --------------------------------------------------------------------------
"""

import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC_CARD = 'normal'
TAG_LIST = ['normal', 'fluid_pound', 'gas_interference', 'gas_lock', 'plunger_stuck', 'solids_grinding', 'solids_in_pump', 'worn_pump']
#TAG_LIST = ['normal', 'fluid_pound', 'gas_lock']
COLOR_LIST = ["#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#DC133C", "#FFA500", "#3CB371", "#8B008B"]
# COLOR_LIST = color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(8)]
CARD_TRANSITION = 20
HEALTH_METRIC = 0.40

# ElasticSearch settings
ES_DIR = os.path.join(os.path.dirname(os.path.join(BASE_DIR)), 'elasticsearch-6.3.2')
ES_BASE_URL= 'http://localhost:9200'
ES_TIMEOUT = 240

# Models settings
MODEL_DIR= os.path.join(os.path.dirname(os.path.join(BASE_DIR)), 'pam_rod_pumps', 'src', 'data_ingestion', 'framework')
AUTOENCODER_NAME = '22032018'
CNN_NAME = '22032018'
ENSEMBLE_L_NAME = '22032018'
ENSEMBLE_RF_NAME = '22032018'
HOG_KNN_NAME = '22032018'
HOG_SVM_NAME = '22032018'
SIAMESE_NAME = '22032018'
ENS_RF_NAME = '22032018'
ENS_LOGIT_NAME = '22032018'

GENERATOR_URL = 'http://localhost:5000/impose'

# -*- coding: utf-8 -*-
"""

@author: Marc Garnica Caparrós
# --------------------------------------------------------------------------
Dash app host
# --------------------------------------------------------------------------
"""
import sys
sys.path.append("../")
sys.path.append("../utils")
import dash
from flask import Flask
from flask_cors import CORS

#Custom modules
import loader as loader

logger = loader.load_logging_info()
app = dash.Dash()
server = app.server
CORS(server)
app.config.suppress_callback_exceptions = True
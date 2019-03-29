import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from plotly.graph_objs import *
import plotly.graph_objs.layout as plotLayout
import plotly.graph_objs as go
import datetime as dt
import numpy as np
import logging
import pandas as pd
import datetime
from ago import human

import loader
from settings import TAG_LIST,HEALTH_METRIC
from app import app


def create_table(pump):
    ''' Return a dash definition of an HTML table for a Pandas dataframe '''
    table = []
    for row in [['hey', 'this', 'is', 'a', 'table'], ['hey', 'this', 'is', 'a', 'table']]:
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table

def generate_well_links():
    # Return a dash definiton of HTML links
    links = []
    well_set = {}
    master = loader.load_master_data()
    for row in master:
        if not row['well'] in well_set:
            well_set[row['well']] = []
        well_set[row['well']].append(row['id'])

    for well in well_set:
        html_link = dcc.Link(well, href='/control/' + str(well))
        links.append(html_link)
        links.append(html.Br())
    return links

def create_well_browser(well_list):
    table = []
    #header
    table.append(html.Tr([html.Th('Well identifier'), html.Th('# Pumps'), html.Th('# Errors')]))
    #rows
    table += [html.Tr([html.Td(dcc.Link(well_list[well]['id'], href='/control/' + str(well_list[well]['id']))),
                       html.Td(well_list[well]['pumps']),
                       html.Td(well_list[well]['errors'], className='table-danger' if well_list[well]['errors'] > well_list[well]['pumps'] / 2 else 'table-success')])
              for well in well_list]
    return table

def get_predicted_data(pump):
    logging.debug('Getting last prediction')
    response = {}
    try:
        query = esutils.query_last_prediction(pump)
        response = es.search(index='predictions', body=query)
        logging.debug(response)
    except Exception:
        logging.exception('Error loading last prediction')

    predicted_data = {}
    predicted_data['label'] = esutils.get_source_value(response, 'pred_label')
    predicted_data['confidence'] = esutils.get_source_value(response, 'pred_conf')
    predicted_data['list_of_scores'] = []
    predicted_data['cycle'] = esutils.get_source_value(response, 'cycle')
    predicted_data['ts'] = esutils.get_source_value(response, 'timestamp')
    for tag in TAG_LIST:
        predicted_data['list_of_scores'].append(esutils.get_source_value(response, tag.replace('_', ' ')))
    return predicted_data

def summary_histogram(list):
    traces = []
    for w in list:
        agg_values = {}
        for pred in list[w]['predicted_data']:
            agg_values[pred['label']] = agg_values.get(pred['label'], 0) + 1
        trace = go.Bar(
            x = TAG_LIST,
            y = [agg_values.get(tag, 0) for tag in TAG_LIST],
            name=w
        )
        traces.append(trace)

    return dcc.Graph(
        id='summary_histo',
        figure={
            'data': traces,
            'layout': {
                'height' : '300',
                'plot_bgcolor': '#fafafa',
                'paper_bgcolor': '#ededed',
                'margin': '0px 0px 0px 0px',
                'barmode': 'stack',
                'title': 'Well summary histogram'
            }
        }, className='col-7'
    )


def get_layout():
    now = datetime.datetime.now()
    master = loader.load_master_data()
    well_list = {}

    for row in master:
        if row['well'] in well_list:
            well_list[row['well']]['pumps'] += 1
            new_data = get_predicted_data(row['id'])
            well_list[row['well']]['predicted_data'].append(new_data)
            if (new_data['label'] != 'normal'):
                well_list[row['well']]['errors'] += 1
        else:
            well = {}
            well['id'] = row['well']
            well['pumps'] = 1
            well['predicted_data'] = []
            new_data = get_predicted_data(row['id'])
            well['predicted_data'].append(new_data)
            if new_data['label'] != 'normal':
                well['errors'] = 1
            else:
                well['errors'] = 0
            well_list[row['well']] = well

    layout = [
        html.Div([
            html.H1("Global overview dashboard", className='col-8 mt-3',),
            html.A(html.Button('Refresh page', className='btn btn-dark'),
                   href='/control/' + str(well), className='col-4 mt-4 text-right'),
        ],
            className='row mb-2 pb-4 align-middle',
            style={'background-color' : '#ffd42e', 'height':'80px'}
        ),
        html.Div([
            html.H6('Updated: ' + now.strftime("%Y-%m-%d %H:%M"), id='last_updated', className='col-12', style={'text-align': 'right'})
        ],
            className='row m-2'
        ),
        html.Div([
            html.Div([
                html.Table(create_well_browser(well_list), className='table-bordered', id='pumps_browser', style={'text-align': 'center', 'width':'100%', 'height':'100%'}),
                ], className='col-5 table-responsive', style={'height':'350px', 'align':'center', 'font-size': '70%'}),
            summary_histogram(well_list)
        ],
            className='row m-2'
        ),
        # Hidden div inside the app that stores the intermediate value
        html.Div(children=json.dumps(well_list), id='global-data', style={'display': 'none'})
    ]
    return layout

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from plotly.graph_objs import *
import plotly.graph_objs.layout as plotLayout
import plotly.graph_objs.scatter as plotScat
import datetime as dt
import numpy as np
import logging
import pandas as pd
import datetime
from ago import human

import loader
from settings import TAG_LIST,HEALTH_METRIC
from app import app



def generate_pump_links(pump_list):
    links = []
    for p in pump_list:
        html_link = dcc.Link(p, href='/pump/' + str(p))
        links.append(html_link)
        links.append(html.Br())
    return links

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

def create_pump_browser(pump_list):
    table = []
    #header
    table.append(html.Tr([html.Th('Pump identifier'), html.Th('Frequency (sec)'), html.Th('Last status'), html.Th('Computed')]))
    #rows
    table += [html.Tr([html.Td(dcc.Link(p['id'], href='/pump/' + str(p['id']))),
                       html.Td(p['freq']),
                       html.Td(p['lp']['label'], className='table-warning' if p['lp']['label'] != 'normal' else 'table-success'),
                       html.Td(human(datetime.datetime.strptime(p['lp']['ts'], "%Y-%m-%dT%H:%M:%S.%f"), 1))])
              for p in pump_list]
    return table

def summary_histogram(list):
    agg_values = {}
    for p in list:
        try:
            query = esutils.query_last_prediction(p['id'])
            response = es.search(index='predictions', body=query)
            agg_values[esutils.get_source_value(response,'pred_label')] = agg_values.get(esutils.get_source_value(response, 'pred_label'), 0) + 1
        except Exception:
            logging.exception('Error loading last prediction')
    return dcc.Graph(
        id='right-bottom-histo',
        figure={
            'data': [{
                'x': TAG_LIST,
                'y': [agg_values.get(tag, 0) for tag in TAG_LIST],
                'type': 'bar'
            }],
            'layout': {
                'height' : '300',
                'plot_bgcolor': '#fafafa',
                'paper_bgcolor': '#ededed',
                'margin': '0px 0px 0px 0px',
                'title': 'Well summary histogram'
            }
        }, className='col-7'
    )

def summary_histogram_test(list):
    agg_values = {}
    for tag in TAG_LIST:
        query = esutils.query_aggregation_by_label(tag)
        try:
            response = es.search(index='predictions', body=query)
            agg_values[tag] = esutils.get_agg_value(response)
        except Exception:
            logging.exception("Error reading the " + tag + " aggregation.")

    return dcc.Graph(
        id='all-histo',
        figure={
            'data': [{
                'x': TAG_LIST,
                'y': [agg_values[tag] for tag in TAG_LIST],
                'type': 'bar'
            }],
            'layout': {
                'paper_bgcolor': '#fafafa',
                'plot_bgcolor': '#ededed',
                'margin': '0px 0px 0px 0px',
                'title': 'Predictions'
            }
        }
    )

def get_layout(well):
    now = datetime.datetime.now()
    master = loader.load_master_data()
    pump_list = []

    for row in master:
        if row['well'] == well:
            row['lp'] = get_predicted_data(row['id'])
            pump_list.append(row)

    layout = [
        html.Div([
            html.A(html.Button('< Back', className='btn btn-dark'),
                   href='/all', className='col-2 mt-4 mb-2'),
            html.H1("Control power dashboard", className='col-6 mt-3',),
            html.A(html.Button('Refresh page', className='btn btn-dark'),
                   href='/control/' + str(well), className='col-4 mt-4 text-right'),
        ],
            className='row mb-2 pb-4 align-middle',
            style={'background-color' : '#ffd42e', 'height':'80px'}
        ),
        html.Div([
            html.H6('Well number: ' + str(well), id='well_number', className='col-4'),
            html.H6('Updated: ' + now.strftime("%Y-%m-%d %H:%M"), id='last_updated', className='col-8', style={'text-align': 'right'})
        ],
            className='row m-2'
        ),
        html.Div([
            html.Div([
                html.Table(create_pump_browser(pump_list), className='table-bordered', id='pumps_browser', style={'text-align': 'center', 'width':'100%', 'height':'100%'}),
                ], className='col-5 table-responsive', style={'height':'350px', 'align':'center', 'font-size': '70%'}),
            summary_histogram(pump_list)
        ],
            className='row m-2'
        ),
        html.Div([
            html.H4('Historical overview', style = {'text-align': 'center', 'width': '100%'})],
            className='row m-0', style={'background-color' : '#ffd42e'}
        ),
        html.Div([
            html.Div(
                [
                    html.P('Filter by date:'),
                    dcc.RadioItems(
                        id='date_selector',
                        options=[
                            {'label': 'All time ', 'value': 'all'},
                            {'label': 'Last year ', 'value': 'year'},
                            {'label': 'Last month ', 'value': 'month'},
                            {'label': 'Last week ', 'value': 'week'},
                            {'label': 'Today ', 'value': 'day'}
                        ],
                        value='all',
                        labelStyle={'display': 'inline-block', 'margin': '10px'}
                    ),
                    html.P('Filter by class:'),
                    html.Button('Check all classes', id='all_button', n_clicks=1),
                    dcc.Dropdown(
                        id='class_dd',
                        options=[{'label': str(t), 'value': str(t)} for t in TAG_LIST],
                        multi=True,
                        value=TAG_LIST
                    )
                ],
                className='col-6'
            ),
            html.Div(
                [
                    dcc.Graph(id='filtered_histogram')
                ],
                className='col-6',
            ),
        ],
            className='row m-2'
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Table(id='monitoring_table', className='table-bordered', style={'text-align': 'center', 'width':'100%', 'height':'100%', 'align':'center', 'font-size': '70%'})
                    ],
                    className='col-12 table-responsive', style={'height' : '350px'},
                ),
            ],
            className='row m-2'
        ),
        # Hidden div inside the app that stores the intermediate value
        html.Div(children=json.dumps(pump_list), id='global-data', style={'display': 'none'})
    ]
    return layout

@app.callback(Output('class_dd', 'value'), [Input('all_button', 'n_clicks')])
def check_all_classes(n_clicks):
    if n_clicks != 0:
        return TAG_LIST

def get_switch_values(key):
    switcher = {
        "all": ["lte", "now/d"],
        "year": ["gte", "now-1y/d"],
        "month": ["gte", "now-1M/d"],
        "week": ["gte", "now-1w/d"],
        "day": ["gte", "now/d"],
    }
    return switcher[key][0], switcher[key][1]

@app.callback(Output('filtered_histogram', 'figure'), [Input('class_dd', 'value'), Input('date_selector', 'value'), Input('global-data', 'children')])
def update_summary_histogram(classes, date_selector, g_data):
    agg_values = {}

    for tag in classes:
        range_label, range_value = get_switch_values(str(date_selector))
        query = esutils.query_aggregation_by_label(tag, range_label, range_value)
        try:
            response = es.search(index='predictions', body=query)
            agg_values[tag] = esutils.get_agg_value(response)
        except Exception:
            logging.exception("Error reading the " + tag + " aggregation.")
    return {
        'data': [{
            'x': classes,
            'y': [agg_values[tag] for tag in classes],
            'type': 'bar'
        }],
        'layout': {
            'autosize' : 'True',
            'plot_bgcolor' : '#fafafa',
            'paper_bgcolor' : '#ededed',
            'margin': '0px 0px 0px 0px',
            'title': 'Predictions'
        }
    }



@app.callback(Output('monitoring_table', 'children'), [Input('class_dd', 'value'), Input('date_selector', 'value'), Input('global-data', 'children')])
def update_monitoring_table(classes, date_selector, g_data):
    j_data = json.loads(g_data)
    dataframe = pd.DataFrame(columns=["%"]+ [p['id'] for p in j_data], index=["error"]+ [str(c) for c in classes])


    for p in j_data:
        agg_values = {}
        total_count = 0.0
        for tag in TAG_LIST:
            range_label, range_value = get_switch_values(str(date_selector))
            query = esutils.query_aggregation_by_label_and_pump(tag, p['id'], range_label, range_value)
            try:
                response = es.search(index='predictions', body=query)
                value = esutils.get_agg_value(response)
                agg_values[tag] = int(value)
                total_count += float(value)
            except Exception:
                logging.exception("Error reading the " + tag + " aggregation.")

        dataframe[p['id']]['error'] = float("{0:.3f}".format(float(total_count - agg_values['normal']) / total_count))
        for c in classes:
            dataframe[p['id']][c] = float("{0:.3f}".format(float(agg_values[c]) / total_count))

    dataframe['%'] = ["error"] + [str(c).replace('_', ' ') for c in classes]

    return [html.Tr([html.Th(col) for col in dataframe.columns], style={'background-color' : '#ffd42e'})] + \
           [html.Tr([html.Td(dataframe.iloc[i][col], className='' if (isinstance(dataframe.iloc[i][col], str) or dataframe.index.values[i] == 'normal') else 'table-success' if dataframe.iloc[i][col] < HEALTH_METRIC else 'table-danger') for col in dataframe.columns])
            for i in range(len(dataframe))]

'''
# Finally not added, function to create a meter chart with a health indicator of the well.

@app.callback(Output('meter', 'figure'), [Input('date_selector', 'value'), Input('global-data', 'children')])
def update_meter(date_selector, g_data):
    agg_values = {}

    range_label, range = get_switch_values(str(date_selector))
    query = esutils.query_aggregation_by_label(tag, range_label, range)
    try:
        response = es.search(index='predictions', body=query)
        agg_values[tag] = esutils.get_agg_value(response)
    except Exception:
        logging.exception("Error reading the " + tag + " aggregation.")

    base_chart = {
        "values": [40, 13, 13, 13, 13, 8],
        "labels": ["-", "0", "30%", "60%", "90%", "100%"],
        "domain": {"x": [0, .48]},
        "marker": {
            "colors": [
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)',
                'rgb(255, 255, 255)'
            ],
            "line": {
                "width": 1
            }
        },
        "name": "Gauge",
        "hole": .4,
        "type": "pie",
        "direction": "clockwise",
        "rotation": 102,
        "showlegend": False,
        "hoverinfo": "none",
        "textinfo": "label",
        "textposition": "outside"
    }

    meter_chart = {
        "values": [50, 14, 14, 14, 8],
        "labels": ["", "Correct", "Warn", "Error", "Fatal"],
        "marker": {
            'colors': [
                'rgb(255, 255, 255)',
                'rgb(121, 255, 77)',
                'rgb(210, 255, 77)',
                'rgb(255, 179, 102)',
                'rgb(255, 102, 102)'
            ]
        },
        "domain": {"x": [0, 0.48]},
        "name": "Gauge",
        "hole": .3,
        "type": "pie",
        "direction": "clockwise",
        "rotation": 90,
        "showlegend": False,
        "textinfo": "label",
        "textposition": "inside",
        "hoverinfo": "none"
    }

    layout = {
        'autosize' : True,
        'xaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'yaxis': {
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False,
        },
        'shapes': [
            {
                'type': 'path',
                'path': 'M 0.235 0.5 L 0.24 0.65 L 0.245 0.5 Z',
                'fillcolor': 'rgba(44, 160, 101, 0.5)',
                'line': {
                    'width': 0.5
                },
                'xref': 'paper',
                'yref': 'paper'
            }
        ],
        'annotations': [
            {
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.23,
                'y': 0.45,
                'text': '50',
                'showarrow': False
            }
        ]
    }

    # we don't want the boundary now
    base_chart['marker']['line']['width'] = 0

    fig = {"data": [base_chart, meter_chart],
           "layout": layout}
    return fig
'''

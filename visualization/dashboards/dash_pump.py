import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
from plotly.graph_objs import *
import plotly.graph_objs.layout as plotLayout
import plotly.graph_objs.scatter as plotScat
import numpy as np
import logging
from datetime import datetime
from ago import human
import random
import requests

#Custom modules
import loader
from settings import TAG_LIST, COLOR_LIST, GENERATOR_URL
from app import app


def get_well_id(pump):
    master = loader.load_master_data()
    for row in master:
        if row['id'] == pump:
            return row['well']
    return False

def create_table(pump, well):
    logging.debug('Creating current status table')
    predicted_data = get_predicted_data(pump)
    table = []

    html_first = []
    html_first.append(html.Td(html.Strong('Pump number')))
    html_first.append(html.Td(pump))
    table.append(html.Tr(html_first))

    html_first = []
    html_first.append(html.Td(html.Strong('Well number')))
    html_first.append(html.Td(well))
    table.append(html.Tr(html_first))

    html_first = []
    html_first.append(html.Td(html.Strong('Status')))
    html_first.append(html.Td(predicted_data['label'].replace('_',' ')))
    table.append(html.Tr(html_first))

    conf = float("{0:.3f}".format(float(predicted_data['confidence'])))
    html_first_p = []
    html_first_p.append(html.Td(html.Strong('Confidence')))
    html_first_p.append(html.Td(conf))
    table.append(html.Tr(html_first_p))

    html_first = []
    html_first.append(html.Td(html.Strong('Last cycle predicted')))
    html_first.append(html.Td(predicted_data['cycle']))
    table.append(html.Tr(html_first))

    timeago = human(datetime.strptime(predicted_data['ts'], "%Y-%m-%dT%H:%M:%S.%f"), 1)
    html_first = []
    html_first.append(html.Td(html.Strong('Last prediction')))
    html_first.append(html.Td(timeago))
    table.append(html.Tr(html_first))


    return table

def create_summary(pump, well, cycle=-1):
    table = []
    logging.debug('Create summary : Updating summary of cycles')
    queryLastCycle = esutils.query_ts_sorted_values(pump=pump, size=1)
    try:
        data = es.search(index='predictions', body=queryLastCycle)
        last_cycle = esutils.get_source_value(data, 'cycle')
        if int(cycle) not in range(-1, int(last_cycle + 1)):
            cycle = -1
        if cycle == -1:
            c = last_cycle
        else:
            c = cycle
        logging.debug('Create summary : Getting summary for cycle %s' % c)
        query = esutils.query_prediction(pump, c)
        res = es.search(index='predictions', body=query)

        table.append(html.Tr([html.Th(html.Strong('Show cycle:', style={'align': 'center'})), html.Th(dcc.Input(value=c, id='summary_cycle', type='number'))], className='thead', style={'background-color' : '#ffd42e'}))

        html_header = []
        html_header.append(html.Th('Class'))
        html_header.append(html.Th('Prediction'))
        table.append(html.Tr(html_header, className='thead'))

        max_pos = 0
        c_pos = 2
        max_value = 0.0
        max_tag = ""
        for tag in TAG_LIST:
            html_row = []
            html_row.append(html.Td(tag.replace('_', ' ')))
            html_row.append(html.Td(esutils.get_source_value(res, tag.replace('_', ' '))))
            if float(esutils.get_source_value(res, tag.replace('_', ' '))) > max_value:
                max_tag = tag.replace('_', ' ')
                max_value = float(esutils.get_source_value(res, tag.replace('_', ' ')))
                max_pos = c_pos
            table.append(html.Tr(html_row))
            c_pos += 1

        html_row = []
        html_row.append(html.Td(max_tag))
        html_row.append(html.Td(max_value))
        table[max_pos]= html.Tr(html_row, className='table-primary')

    except Exception as e:
        logging.exception('Create summary : Error querying for last cycle')
    return table

def json_data(p,w):
    data = {
        "pump" : p,
        "well" : w
    }
    return json.dumps(data)

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

def get_layout(pump):
    logging.debug('New request for pump %s' % pump)
    well = get_well_id(pump)
    if not well:
        logging.debug('Pump does not exist')
        return '404'
    layout = [
        html.Div([
            html.A(html.Button('< Back', className='btn btn-dark'),
                   href='/control/' + str(well), className='col-2 mt-4 mb-2'),
            html.H1("Pump status dashboard", className='col-6 mt-3'),
            html.P("Impose error: ", id='impose_label', className='col-2 mt-4 text-right'),
            html.Div([
                dcc.Dropdown(
                    id='impose_dd',
                    options = [{'label': 'Nothing', 'value': 'Nothing'}] + [{'label': str(t), 'value': str(t)} for t in TAG_LIST],
                    value='Nothing',
                    className='inline-block mt-4'
                )],
                className="col-2",
            ),
            ],
            className='row mb-2 pb-4 align-middle',
            style={'background-color' : '#ffd42e', 'height':'80px'}
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='pump')
                ], className='col-6'
            ),
            dcc.Interval(id='info-rt-update', interval=2000, n_intervals=0),
            html.Div([
                html.Div([
                    dcc.Interval(id='info-update', interval=10000, n_intervals=0),
                    html.Div([
                        html.Table(create_table(pump,well), id='status_table', style={'align':'center', 'font-size': '70%'}, className='table-sm table-bordered')
                    ], className='table-responsive col-4'),
                    html.Div([
                        dcc.Graph(id='radar-pump'),
                        ], className='col-8')
                    ],
                    className='row'
                )
                ],
                className='col-6'
            )
            ],
            className='row mt-4 mb-4'
        ),
        html.Div([
            html.Div([
                #dcc.Input(id='summary_cycle', type='number'),
                html.Table(create_summary(pump,well), id='summary_table', style={'align': 'center', 'height': '100%', 'font-size': '60%'}, className='table')
            ], className='col-4'
            ),
            html.Div([
                dcc.Graph(id='prob-series')
            ], className='col-8'
            )
        ],
            className='row mt-4 mb-4'
        ),
        # Hidden div inside the app that stores the intermediate value
        html.Div(children=json_data(pump,well), id='global-data', style={'display': 'none'})
    ]
    return layout

@app.callback(
    Output('pump', 'figure'),
    [Input('info-rt-update', 'n_intervals'),
     Input('global-data', 'children')])
def gen_pump_card(interval, data):
    j_data = json.loads(data)
    current_pump = j_data['pump']
    current_well = j_data['well']
    logging.debug('Updating current pump: %s' % (current_pump))

    queryLastCycle = esutils.query_ts_sorted_values(pump=current_pump, size=1)
    data = es.search(index=current_well.lower(), body=queryLastCycle)
    lastCycle = esutils.get_source_value(data,'cycle')
    if lastCycle is not None:
        logging.critical('Last Cycle of the pump: %s' % lastCycle)
        lastPos = esutils.get_source_value(data, 'position')
        lastForce = esutils.get_source_value(data, 'force')
        logging.critical('Current point (%s, %s)' % (lastPos, lastForce))

        if lastPos is not None and lastForce is not None:
            queryCycleValues = esutils.query_cycle_values(pump=current_pump, cycle=lastCycle)
            data = es.search(index=current_well.lower(), body=queryCycleValues)
            selected_cycle_values = esutils.get_source_vector_value(data, 'position', 'force')
            logging.debug("Last cycle data received:")
            logging.debug("Size of vector postion = %s" % len(selected_cycle_values['position']))
            logging.debug("Size of vector force = %s" % len(selected_cycle_values['force']))

            if selected_cycle_values is not None:
                cycle_trace = Scatter(
                    x=selected_cycle_values['position'],
                    y=selected_cycle_values['force'],
                    name='Cycle %i' % (lastCycle),
                    mode='lines+markers'
                )

                current_point = Scatter(
                    x=np.array(lastPos),
                    y=np.array(lastForce),
                    name='Last point',
                    mode='markers'
                )

                layout = Layout(
                    height=350,
                    xaxis=dict(
                        range=[0, 1],
                        fixedrange=True,
                        title='Position'
                    ),
                    yaxis=dict(
                        range=[0,1],
                        fixedrange=True,
                        zeroline=False,
                        title='Force'
                    ),
                    margin=plotLayout.Margin(
                        t=60,
                        l=50,
                        r=40,
                        b=60
                    ),
                    plot_bgcolor="#fafafa",
                    paper_bgcolor="#ededed",
                    title='Current card plot'
                )
                return Figure(data=[cycle_trace, current_point], layout=layout)
    return None

@app.callback(
    Output('radar-pump', 'figure'),
    [Input('info-update', 'n_intervals'),
     Input('global-data', 'children')])
def gen_pump_radar(intervals,data):
    j_data = json.loads(data)
    predicted_data = get_predicted_data(j_data['pump'])
    sdata = [Scatterpolar(
        r=predicted_data['list_of_scores'],
        theta=TAG_LIST,
        fill='toself'
    )]
    layout = Layout(
        height=350,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        plot_bgcolor="#fafafa",
        paper_bgcolor="#ededed",
        title='Prediction distribution'
    )
    return Figure(data=sdata, layout=layout)


@app.callback(
    Output('prob-series', 'figure'),
    [Input('info-update', 'n_intervals'),
     Input('global-data', 'children')])
def gen_prob_series(intervals,data):
    j_data = json.loads(data)
    predicted_data = get_predicted_data(j_data['pump'])
    lastCycle = int(predicted_data['cycle'])
    query = esutils.query_last_prediction(j_data['pump'], 50)
    response = es.search(index='predictions', body=query)
    data = []
    for tag in TAG_LIST:
        results = esutils.get_source_vector_value(response, tag.replace('_',' '), 'cycle')
        color = COLOR_LIST[TAG_LIST.index(tag)]
        trace = Scatter(
            y=results[tag.replace('_', ' ')],
            x=results['cycle'],
            line=plotScat.Line(
                color=color
            ),
            name=tag,
            mode='lines'
        )

        data.append(trace)
    layout = Layout(
        autosize=True,
        yaxis=dict(
            range=[0, 1],
            fixedrange=True,
            title='Results'
        ),
        xaxis=dict(
            #range=[max(0, lastCycle - 30), lastCycle],
            autorange=True,
            zeroline=False,
            title='Cycle',
            tickformat=',d'
        ),
        margin=plotLayout.Margin(
            t=45,
            l=50,
            r=50
        ),
        plot_bgcolor="#fafafa",
        paper_bgcolor="#ededed",
        title='Status evolution'
    )

    return Figure(data=[t for t in data], layout=layout)


@app.callback(
    Output('summary_table', 'children'),
    [Input('info-update', 'n_intervals'),
     Input('global-data', 'children'),
     Input('summary_cycle', 'value')])
def update_summary_table(interval, data, cycle):
    logging.debug(' Update summary: New cycle request for cycle %s' % cycle)
    j_data = json.loads(data)
    if not cycle:
        cycle = -1
    return create_summary(j_data['pump'], j_data['well'], cycle)

@app.callback(
    Output('status_table', 'children'),
    [Input('info-update', 'n_intervals'),
     Input('global-data', 'children')])
def update_summary_table(interval, data):
    logging.debug(' Update status')
    j_data = json.loads(data)
    return create_table(j_data['pump'], j_data['well'])

@app.callback(
    Output('impose_label', 'value'),
    [Input('impose_dd', 'value'),
     Input('global-data', 'children')])
def impose_error(imposed_error, data):
    j_data = json.loads(data)
    print(imposed_error)
    try:
        if imposed_error != 'Nothing':
            payload = {
                'pump' : j_data['pump'],
                'imposed': imposed_error
            }
            r = requests.post(GENERATOR_URL, params=payload)
            logging.debug(r)
            return 'Imposed error: '
    except Exception:
        logging.exception('Error modifying the generator of data')

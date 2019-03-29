import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
import plotly.graph_objs as go
import plotly.plotly as py
import datetime as dt
import numpy as np
import logging
import pandas as pd
import datetime
from ago import human
import os

import loader
from settings import TAG_LIST,HEALTH_METRIC
from app import app


weak_gray = '#e6e6e6'
strong_gray = '333333'
orange = 'f06137'
soft_organe = 'ff8964'


def draw_court_chart():
    img_width = 1600
    img_height = 900
    scale_factor = 0.5
    logging.debug("hey")

    layout = go.Layout(
        xaxis=go.layout.XAxis(
            visible=False,
            range=[0, img_width * scale_factor]),
        yaxis=go.layout.YAxis(
            visible=False,
            range=[0, img_height * scale_factor],
            # the scaleanchor attribute ensures that the aspect ratio stays constant
            scaleanchor='x'),
        width=img_width * scale_factor,
        height=img_height * scale_factor,
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0},
        images=[go.layout.Image(
            visible=True,
            x=img_width,
            sizex=img_width * scale_factor,
            y=img_height * scale_factor,
            sizey=img_height * scale_factor,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source='file:///home/marc/Development/thesis/data_browser/res/court_basic.png')]
    )

    fig = go.Figure(data=[{
        'x': [0, img_width * scale_factor],
        'y': [0, img_height * scale_factor],
        'mode': 'markers',
        'marker': {'opacity': 0}}], layout=layout)

    return dcc.Graph(
        id='court_chart',
        figure=fig
    )


def get_layout():
    layout = [
        html.Div([
            html.A(html.Button('Home', className='btn btn-dark'),
                   href='/control/hola', className='col-2 mt-4 mb-2'),
            html.H1("Data browser", className='col-6 mt-3'),
            ],
            className='row mb-2 pb-4 align-middle',
            style={'background-color' : weak_gray, 'height':'80px'}
        ),
        html.Div([
            html.Div([
                draw_court_chart()
                ], className='col-6'
            )
        ])
    ]
    return layout

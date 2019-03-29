# -*- coding: utf-8 -*-
"""

@author: Marc Garnica Caparrós
# --------------------------------------------------------------------------
Dash app routing functionalities
# --------------------------------------------------------------------------
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
import logging
from dashboards import main_dashboard

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', className='container-fluid', style={'font-family': 'Graphik !important', 'height': '100%', 'text-rendering': 'optimizeLegibility'})
])

external_css = ["https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css", ]

for css in external_css:
    app.css.append_css({"external_url": css})


# Routing of the app
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    try:
        if pathname == '/' or pathname == '/all':
            return main_dashboard.get_layout()

        else:
            return '404'
    except Exception as e:
        logging.exception('Error routing the pages')
        return '404'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, threaded=True)

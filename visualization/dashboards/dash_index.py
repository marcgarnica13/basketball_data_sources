import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    dcc.Link('Main dashboard', href='/main'),
    html.Br(),
    dcc.Link('Pump dashboard', href='/pump/1A'),
    html.Br(),
    dcc.Link('Well dashboard', href='/well/A'),
    html.Br(),
    dcc.Link('Index of dashboards', href='/index'),
])
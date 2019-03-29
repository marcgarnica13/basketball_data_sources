import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs.layout as plot_layout

import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv')
df['text'] = df['airport'] + '' + df['city'] + ', ' + df['state'] + '' + 'Arrivals: ' + df['cnt'].astype(str)

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

data = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = df['long'],
        lat = df['lat'],
        text = df['text'],
        mode = 'markers'
        )]
map_layout = dict(
            title = 'Title',
            margin=plot_layout.Margin(
            l=10,r=10, b=10, t=50, pad=4
        ),
            geo = dict(
                scope='world',
                showframe = True,
                projection = dict(type='enumerated : "equirectangular"'),
                showcountries=True,
                showsubunits=True,
                showocean=True,
                countrycolor='green',
                oceancolor='#aec6cf'
            )
)

fig = dict(data=data, layout=map_layout)

layout = html.Div([
    dcc.Graph(id='well_mundi', figure=fig)
])
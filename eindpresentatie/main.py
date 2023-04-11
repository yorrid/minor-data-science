from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import yfinance as yf
import dash_bootstrap_components as dbc
import geopandas as gpd
from urllib.request import urlopen
import json

# Set css
dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'

# Mapbox token
px.set_mapbox_access_token('pk.eyJ1IjoieW9ycmlkIiwiYSI6ImNsZnV3cHllejAxazUzZ2x5Y25ua29jbnIifQ.DaEnA0YRKUq6q5eNbj-o0g')

# Load data
emissions = pd.read_csv('co2_emissions_kt_by_country.csv')
region = pd.read_csv('Methane_final.csv')
gdp = pd.read_csv('world_country_gdp_usd.csv')
pop = pd.read_csv('population_by_country_2020.csv')

region = region.drop(columns=['Unnamed: 0'])

gdp.columns = gdp.columns.str.replace(' ', '_')
gdp.columns = gdp.columns.str.lower()

pop = pop.rename(columns={'Country (or dependency)': 'country', 'Population (2020)': 'population', 'Density (P/Km²)': 'density', 
                          'Land Area (Km²)': 'land_area', 'Migrants (net)': 'migrants', 'Fert. Rate': 'fert_rate', 'Med. Age': 'med_age', 'Urban Pop %': 'urban_pop',
                          'Yearly Change': 'yearly_change', 'World Share': 'world_share'})


with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
    geo = json.load(response)
geo = gpd.GeoDataFrame.from_features(geo['features'])
geo = geo.rename(columns={'ADMIN': 'country'})

# merge emissions and gdp
merge = pd.merge(emissions, gdp, left_on='country_code', right_on='country_code', how='inner')
merge = merge.drop(columns=['country_name_y', 'year_y'])
merge = merge.rename(columns={'country_name_x': 'country_name', 'year_x': 'year'})
sec_merge = pd.merge(merge, region, left_on='country_name', right_on='country', how='inner')
final_merge = pd.merge(sec_merge, pop, left_on='country_name', right_on='country', how='inner')
emissions_gdp = final_merge.copy()

# Clean data
emissions_gdp = emissions_gdp.drop(columns=['country_x','country_y' , 'type', 'segment', 'reason', 'baseYear', 'notes'])
emissions_gdp = emissions_gdp.rename(columns={'country_name': 'country', 'value': 'co2_emissions', 'gdp_usd': 'gdp', 
                                              'gdp_per_capita_usd':'gdp_per_capita', 'emissions':'methane_emissions'})
emissions_gdp = emissions_gdp[emissions_gdp['year'] >= 2000]


# Create app`
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

# Create layout
app.layout = \
html.Div([
    html.Center([
        html.Div([html.H1('Eindpresentatie'),]),
    ]),

    html.Div([
        html.H3('Histograms'),
        html.Hr(),
        html.Br(),
        html.Div([
            html.Center(html.B('Select the preffered data to display on each of the the histograms:')),
            dcc.RadioItems(
                id='radio_emissions',
                options=[{'label': 'GDP per capita', 'value': 'gdp_per_capita'}, {'label': 'CO2 emissions', 'value': 'co2_emissions'}, 
                {'label': 'Methane emissions', 'value': 'methane_emissions'}],
                value='gdp_per_capita', style={'display': 'inline-block', 'margin-left': '20px'}, className='dbc'
            ),
            dcc.RadioItems(
                id='radio_population',
                options=[{'label': 'GDP per capita', 'value': 'gdp_per_capita'}, {'label': 'Population', 'value': 'population'}, 
                {'label': 'Population density', 'value': 'density'}],
                value='gdp_per_capita', style={'display': 'inline-block', 'float': 'right', 'margin-right': '20px'}, className='dbc',
            ),
        ]),
        html.Br(),
        html.Div([
            dcc.Graph(id='histogram_emissions', style={'display': 'inline-block', 'width': '49%'}),
            dcc.Graph(id='histogram_population', style={'display': 'inline-block', 'width': '49%'}),
        ]),
    ]),

    html.Div([
       html.H3('Scatterplot'),
        html.Hr(),
        html.Br(),
        html.Div([  
            html.B('Select the preffered data to display on the scatterplot:', style={'margin-left':'20px'}),
            dcc.RadioItems(
                id='radio_scatter',
                options=[{'label': 'CO2 emissions', 'value': 'co2_emissions'}, 
                {'label': 'Methane emissions', 'value': 'methane_emissions'}],
                value='co2_emissions', style={'margin-left':'20px'}, className='dbc'
            ),
        ]),
        html.Div([
            dcc.Graph(id='scatterplot',),
        ]),
    ]),

    html.Div([html.Br(),
            html.H3('Choropleth map'),
            ]),

    html.Center([
        html.Div([
            html.Hr(),
            html.Br(),
            html.B('Select the preffered data to display on the map:'),
            dcc.Dropdown(
                id='emissions', 
                className='dbc',
                options=[{'label': 'CO2 emission', 'value': 'co2_emissions'}, {'label': 'Methane emission', 'value': 'methane_emissions'},
                        {'label': 'Population', 'value': 'population'}, {'label': 'GDP per capita', 'value': 'gdp_per_capita'}],
                multi=False,
                value="co2_emissions",
                style={'width': "50%"}
            ),
            html.Br(),
            dcc.Graph(id='choropleth'),
            dcc.Slider(
                id='year-slider',
                min=emissions_gdp['year'].min(),
                max=emissions_gdp['year'].max(),
                value=emissions_gdp['year'].max(),
                marks={str(year): str(year) for year in emissions_gdp['year'].unique()},
                className='dbc',
            ),
        ])
    ])
])

# Create callbacks
@app.callback(
    Output('choropleth', 'figure'),
    [Input('emissions', 'value'), Input('year-slider', 'value')]
)

def update_choropleth(value, year):

    data = emissions_gdp[emissions_gdp['year'] == year]

    if value == "co2_emissions":
        fig = px.choropleth_mapbox(data, geojson=geo, featureidkey = 'properties.ISO_A3',
                           locations='country_code', color='co2_emissions',
                           color_continuous_scale="Viridis",
                           labels={'co2_emissions': f'CO2 emissions {year} (kt)'},
                           height=600, width=1500, center={"lat":40.547395, "lon":11.277328}, zoom=0.5, range_color=(0, 5000000),
                          )
    elif value == "methane_emissions":
        fig = px.choropleth_mapbox(data, geojson=geo, featureidkey = 'properties.ISO_A3',
                        locations='country_code', color='methane_emissions',
                        color_continuous_scale="Viridis",
                        labels={'methane_emissions': f'Methane emissions {year} (kt)'},
                        height=600, width=1500, center={"lat":40.547395, "lon":11.277328}, zoom=0.5, range_color=(0, 11000),
                        )
    elif value == "population":
        fig = px.choropleth_mapbox(data, geojson=geo, featureidkey = 'properties.ISO_A3',
                        locations='country_code', color='population',
                        color_continuous_scale="Viridis",
                        labels={'population': f'Population in {year}'},
                        height=600, width=1500, center={"lat":40.547395, "lon":11.277328}, zoom=0.5,
                        )
    elif value == "gdp_per_capita":
        fig = px.choropleth_mapbox(data, geojson=geo, featureidkey = 'properties.ISO_A3',
                        locations='country_code', color='gdp_per_capita',
                        color_continuous_scale="Viridis",
                        labels={'gdp_per_capita': f'GDP per capita in {year}'},
                        height=600, width=1500, center={"lat":40.547395, "lon":11.277328}, zoom=0.5,
                        )
        
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


@app.callback(
    Output('histogram_emissions', 'figure'),
    [Input('radio_emissions', 'value')]
)

def update_histogram(value):
    hist_data = emissions_gdp.loc[(emissions_gdp['year'] == 2019) & (emissions_gdp['co2_emissions'] > 200000)]

    fig = px.histogram(hist_data, x='country', y=value, color='region', hover_data=hist_data.columns, height=600,
                       labels={'country': 'Country', 'region': 'Region', 'gdp_per_capita': 'GDP per capita in 2019 (USD)',
                               'co2_emissions': 'CO2 emissions in 2019 (kt)', 'methane_emissions': 'Methane emissions in 2019 (kt)'}, title='Histogram of emissions')
    
    return fig

@app.callback(
    Output('histogram_population', 'figure'),
    [Input('radio_population', 'value')]
)

def update_histogram(value):
    hist_data = emissions_gdp.loc[(emissions_gdp['year'] == 2019) & (emissions_gdp['co2_emissions'] > 200000)]

    fig = px.histogram(hist_data, x='country', y=value, color='region', hover_data=hist_data.columns, height=600,
                       labels={'country': 'Country', 'region': 'Region', 'gdp_per_capita': 'GDP per capita in 2019 (USD)',
                               'population': 'Population in 2019', 'density': 'Population density in 2019 (people/km2)',}, title='Histogram of population')
    
    return fig

@app.callback(
    Output('scatterplot', 'figure'),
    [Input('radio_scatter', 'value')]
)

def update_scatter(value):
   
   if value == "co2_emissions":
    fig = px.scatter(emissions_gdp, x='year', y=value, color='region', 
                                                            labels={'year': 'Year', 'co2_emissions': 'CO2 emissions (kt)', 'region': 'Region', 
                                                                    'gdp_per_capita': 'GDP per capita (USD)', 'population': 'Population', },
                                                            title='CO2 emissions by region over the years', hover_name='country', 
                                                            hover_data=['gdp_per_capita', 'population', 'co2_emissions'],)
   elif value == "methane_emissions":
       fig = px.scatter(emissions_gdp, x='year', y=value, color='region', 
                                                            labels={'year': 'Year', 'region': 'Region', 
                                                                    'gdp_per_capita': 'GDP per capita (USD)', 'population': 'Population', 
                                                                    'methane_emissions': 'Methane emissions (kt)'},
                                                            title='Methane emissions by region over the years', hover_name='country', 
                                                            hover_data=['gdp_per_capita', 'population', 'methane_emissions'],)
   

   return fig

# Execute app
if __name__ == '__main__':
    app.run_server(debug=True)
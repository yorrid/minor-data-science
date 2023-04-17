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
df = final_merge.copy()

# Clean data
df = df.drop(columns=['country_x','country_y' , 'type', 'segment', 'reason', 'baseYear', 'notes'])
df = df.rename(columns={'country_name': 'country', 'value': 'co2_emissions', 'gdp_usd': 'gdp', 
                                              'gdp_per_capita_usd':'gdp_per_capita', 'emissions':'methane_emissions'})
df = df[df['year'] >= 2000]
df = df.drop_duplicates(subset=['country', 'year', 'gdp_per_capita'])
df = df.dropna()

# Change region of Australia to Oceania
df.loc[df['country'] == 'Australia', 'region'] = 'Oceania'


df_show = df.sample(n = 300)

# Create app`
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])

# Create layout
app.layout = (
dcc.Tabs(
        id="tabs-with-classes",
        value='tab-1',
        className='custom-tabs-container',children=[
    dcc.Tab(
        label='Data',
        value='tab-1',
        className='custom-tab',
        selected_className='custom-tab--selected', children=[
        html.Div([
            html.Center([
                html.Div([html.H1('De data'),]),
                dash_table.DataTable(
                    id='datatable',
                    columns=[{"name": i, "id": i} for i in df_show.columns],
                    data=df_show.to_dict('records'),
                    style_cell={'textAlign': 'left', 'minWidth': '0px', 'maxWidth': '180px', 'whiteSpace': 'normal'},
                    style_table={'overflowX': 'scroll'},
                    filter_action="native", sort_action="native", sort_mode="multi", page_action="native", page_current=0, page_size=10,
                        style_cell_conditional=[
                                {
                                    'if': {'column_id': c},
                                    'textAlign': 'left'
                                } for c in ['Date', 'Region']
                            ],
                            style_data={
                                'color': 'black',
                                'backgroundColor': 'white'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(220, 220, 220)',
                                }
                            ],
                            style_header={
                                'backgroundColor': 'rgb(210, 210, 210)',
                                'color': 'black',
                                'fontWeight': 'bold'
                            }    
                )
            ]),
        ]),
    ]),
    dcc.Tab(
        label='Histograms',
        value='tab-2',
        className='custom-tab',
        selected_className='custom-tab--selected', children=[
        html.Div([
            html.Center(html.H3('Histograms')),
            html.Hr(),
            html.Br(),
            html.Div([
                html.Center(html.B('Select the preffered data to display on each of the histogram:')),
                html.Br(),
                html.Div(className='radio-container' , children=[
                    dcc.RadioItems(
                        id='radio_emissions',
                        options=[{'label': 'GDP per capita', 'value': 'gdp_per_capita'}, {'label': 'CO2 emissions', 'value': 'co2_emissions'}, 
                        {'label': 'Methane emissions', 'value': 'methane_emissions'}],
                        value='gdp_per_capita', style={'display': 'inline-block', 'margin-left': '20px'}, className='radio',
                    ),
                    dcc.RadioItems(
                        id='radio_population',
                        options=[{'label': 'GDP per capita', 'value': 'gdp_per_capita'}, {'label': 'Population', 'value': 'population'}, 
                        {'label': 'Population density', 'value': 'density'}],
                        value='gdp_per_capita', style={'display': 'inline-block', 'float': 'right', 'margin-right': '20px'}, className='radio',
                    ),
                ]),
            ]),
            html.Br(),
            html.Div([
                dcc.Graph(id='histogram_emissions', style={'display': 'inline-block', 'width': '49%'}),
                dcc.Graph(id='histogram_population', style={'display': 'inline-block', 'width': '49%'}),
            ]),
            html.Br(),
            html.Hr(),
            html.Br(),
            html.Div([
                html.B('Select the preffered distribution to display on the histogram:', style={'margin-left':'20px'}),
                dcc.RadioItems(
                id='distribution',
                options=[{'label':'Box', 'value':'box'}, {'label':'Violin', 'value':'violin'}, {'label':'Rug', 'value':'rug'}, {'label':'None', 'value':False,}],
                value='box', className='radio', style={'margin-left':'20px', 'width':'20%'}
                ),
                dcc.Graph(id='histogram_distribution'),
            ])
        ]),
    ]),
    dcc.Tab(
        label='Scatterplot', 
        value='tab-3',
        className='custom-tab',
        selected_className='custom-tab--selected',children=[
        html.Div([
        html.Center(html.H3('Scatterplot')),
            html.Hr(),
            html.Br(),
            html.Div([  
                html.B('Select the preffered data to display on the scatterplot:', style={'margin-left':'20px'}),
                dcc.RadioItems(
                    id='radio_scatter',
                    options=[{'label': 'CO2 emissions', 'value': 'co2_emissions'}, 
                    {'label': 'Methane emissions', 'value': 'methane_emissions'}],
                    value='co2_emissions', style={'margin-left':'20px', 'width':'20%'}, className='radio'
                ),
            ]),
            html.Div([
                dcc.Graph(id='scatterplot',),
            ]),
        ]),
    ]),
    dcc.Tab(
        label='Choropleth map', 
        value='tab-4',
        className='custom-tab',
        selected_className='custom-tab--selected',children=[
        html.Center([
            html.Div([
                html.H3('Choropleth map'),
                html.Hr(),
                html.Br(),
                html.B('Select the preffered data to display on the map:'),
                dcc.Dropdown(
                    id='emissions', 
                    className='dropdown',
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
                    min=df['year'].min(),
                    max=df['year'].max(),
                    value=df['year'].max(),
                    marks={str(year): str(year) for year in df['year'].unique()},
                    className='dbc',),
                ])
            ])
        ])
    ])    
)

# Create callbacks
@app.callback(
    Output('choropleth', 'figure'),
    [Input('emissions', 'value'), Input('year-slider', 'value')]
)

def update_choropleth(value, year):

    data = df[df['year'] == year]

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
    hist_data = df.loc[(df['year'] == 2019) & (df['co2_emissions'] > 200000)]

    fig = px.histogram(hist_data, x='country', y=value, color='region', hover_data=hist_data.columns, height=600,
                       labels={'country': 'Country', 'region': 'Region', 'gdp_per_capita': 'GDP per capita in 2019 (USD)',
                               'co2_emissions': 'CO2 emissions in 2019 (kt)', 'methane_emissions': 'Methane emissions in 2019 (kt)'}, title='Histogram of emissions')
    
    return fig

@app.callback(
    Output('histogram_population', 'figure'),
    [Input('radio_population', 'value')]
)

def update_histogram(value):
    hist_data = df.loc[(df['year'] == 2019) & (df['co2_emissions'] > 200000)]

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
    fig = px.scatter(df, x='year', y=value, color='region', 
                                                            labels={'year': 'Year', 'co2_emissions': 'CO2 emissions (kt)', 'region': 'Region', 
                                                                    'gdp_per_capita': 'GDP per capita (USD)', 'population': 'Population', },
                                                            title='CO2 emissions by region over the years', hover_name='country', 
                                                            hover_data=['gdp_per_capita', 'population', 'co2_emissions'],)
   elif value == "methane_emissions":
       fig = px.scatter(df, x='year', y=value, color='region', 
                                                            labels={'year': 'Year', 'region': 'Region', 
                                                                    'gdp_per_capita': 'GDP per capita (USD)', 'population': 'Population', 
                                                                    'methane_emissions': 'Methane emissions (kt)'},
                                                            title='Methane emissions by region over the years', hover_name='country', 
                                                            hover_data=['gdp_per_capita', 'population', 'methane_emissions'],)
   

   return fig

@app.callback(
    Output('histogram_distribution', 'figure'),
    [Input('distribution', 'value')]
)

def update_dist(value):
    hist_data = df.loc[(df['year'] == 2019) & (df['co2_emissions'] > 200000)]

    fig = px.scatter(hist_data, x='country', y='gdp_per_capita', color='region', hover_data=hist_data.columns, height=600, marginal_y=value,
                       labels={'country': 'Country', 'region': 'Region', 'gdp_per_capita': 'GDP per capita in 2019 (USD)'}, title='Distribution of gdp per capita')
    
    return fig





# Execute app
if __name__ == '__main__':
    app.run_server(debug=True)
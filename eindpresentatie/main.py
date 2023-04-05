from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import yfinance as yf
import dash_bootstrap_components as dbc

# Load data
emissions = pd.read_csv('co2_emissions_kt_by_country.csv')
region = pd.read_csv('Methane_final.csv')
gdp = pd.read_csv('world_country_gdp_usd.csv')
school = pd.read_csv('mean-years-of-schooling-long-run.csv', delimiter=';')

# Make data ready for merge
region = region.drop(columns=['Unnamed: 0'])

gdp.columns = gdp.columns.str.replace(' ', '_')
gdp.columns = gdp.columns.str.lower()

school.columns = school.columns.str.replace(' ', '_')

# Merge data
merge = pd.merge(emissions, gdp, left_on='country_code', right_on='country_code', how='inner')
merge = merge.drop(columns=['country_name_y', 'year_y'])
merge = merge.rename(columns={'country_name_x': 'country_name', 'year_x': 'year'})
emissions_gdp = pd.merge(merge, region, left_on='country_name', right_on='country', how='inner')

# Clean data
emissions_gdp = emissions_gdp.drop(columns=['country', 'emissions', 'type', 'segment', 'reason', 'baseYear', 'notes'])

# Create app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = \
html.Div([
    html.H1('Eindpresentatie VA'),

])
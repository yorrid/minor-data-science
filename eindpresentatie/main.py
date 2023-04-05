from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import yfinance as yf
import dash_bootstrap_components as dbc

# Load data
emissions = pd.read_csv('Methane_final.csv')
gdp = pd.read_csv('world_country_gdp_usd.csv')
school = pd.read_csv('mean-years-of-schooling-long-run.csv', delimiter=';')

# Clean data
emissions = emissions.drop(columns=['Unnamed: 0'])

# Create app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout

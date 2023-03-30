import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime as dt
import geopandas as gpd
import streamlit as st
import streamlit.components.v1 as components
import json

# Folium mapping function
def folium_static(fig,width=700, height=500):

    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)

        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
        )

# Data loading and cleaning

## Data load
df = pd.read_excel('/ext/MDS_2023-1_hackathon/groep_01/Locatievoorstellen.xlsx', header=1)
tijd_per_pc = pd.read_csv('/ext/MDS_2023-1_hackathon/groep_01/tijd_per_pc.csv')
geofile = gpd.read_file('/ext/MDS_2023-1_hackathon/groep_01/postcode.geojson')
pd.set_option('display.max_columns', None)

## Column cleaning
df.columns = df.columns.str.replace(' - ', '_')
df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.lower()
df = df.drop(columns=['stilgezet_uitleg','verplaatsing_mra-e_laadpaal_id', 'opmerkingen', 'toelichting_bij_verplaatsing', 
                      'locatiecode', 'aanbodgestuurd_opmerkingen', 'datagestuurd_opmerkingen', 'gemeente_akkoord_met_offerte_verplaatsing',
                     'extra_laadpaal_ids', 'referenties', 'aanleiding'])

### Change column to datetime
df["tijdstip_van_laatste_wijziging"] = pd.to_datetime(df["tijdstip_van_laatste_wijziging"])
df["tijdstip_aangemaakt"] = pd.to_datetime(df["tijdstip_aangemaakt"])
df["tijdstip_locatievoorstel"] = pd.to_datetime(df["tijdstip_locatievoorstel"])
df["tijdstip_controle_locatievoorstel"] = pd.to_datetime(df["tijdstip_controle_locatievoorstel"])
df["tijdstip_advies_exploitant"] = pd.to_datetime(df["tijdstip_advies_exploitant"])
df["tijdstip_publicatie_verkeersbesluit"] = pd.to_datetime(df["tijdstip_publicatie_verkeersbesluit"])
df["tijdstip_aanvraag_netaansluiting"] = pd.to_datetime(df["tijdstip_aanvraag_netaansluiting"])
df["tijdstip_definitief_verkeersbesluit"] = pd.to_datetime(df["tijdstip_definitief_verkeersbesluit"])
df["tijdstip_accepteren_mra-e"] = pd.to_datetime(df["tijdstip_accepteren_mra-e"])
df["tijdstip_realisatie_plannen"] = pd.to_datetime(df["tijdstip_realisatie_plannen"])
df["tijdstip_locatie_voorbereiden"] = pd.to_datetime(df["tijdstip_locatie_voorbereiden"])
df["tijdstip_in_bedrijf"] = pd.to_datetime(df["tijdstip_in_bedrijf"])
df["tijdstip_opleveren_laadpaal"] = pd.to_datetime(df["tijdstip_opleveren_laadpaal"])
df["tijdstip_opleveren_locatie"] = pd.to_datetime(df["tijdstip_opleveren_locatie"])
for column in df.select_dtypes(include=[np.datetime64]).columns:
    df[column] = df[column].dt.strftime('%Y-%m-%d')
    df[column] = pd.to_datetime(df[column])

### Adjusting postcode data
df['postcode'] = df['postcode'].str.replace('[a-zA-Z]', '', regex=True)
df['postcode'] = df['postcode'].str.replace(' ', '', regex=True)
df['postcode'] = df['postcode'].astype(int)

### Create new columns
df['datum_oplevering_y'] = pd.DatetimeIndex(df['datum_oplevering']).year
df['datum_oplevering_y'] = df['datum_oplevering_y'].fillna(0).astype(int)
df.loc[(df['datum_oplevering_y'] == 0), 'datum_oplevering_y'] = None
df = df.loc[(df['datum_oplevering_y'] < 2024)]

df['tijd_a_b'] = (df['tijdstip_controle_locatievoorstel'] - df['tijdstip_aangemaakt']).dt.days
df['tijd_b_c'] = (df['tijdstip_aanvraag_netaansluiting'] - df['tijdstip_controle_locatievoorstel']).dt.days
df['tijd_c_d'] = (df['tijdstip_definitief_verkeersbesluit'] - df['tijdstip_publicatie_verkeersbesluit']).dt.days
df['tijd_totaal'] = (df['tijdstip_opleveren_locatie'] - df['tijdstip_aangemaakt']).dt.days

df.loc[(df['stilgezet'] == False) & df['tijd_totaal'].notna(), ['exploitant_akkoord', 'aannemer_akkoord', 'gemeente_akkoord']] = True
df.loc[(df['stilgezet'] == True) | df['tijd_totaal'].isna(), ['exploitant_akkoord', 'aannemer_akkoord', 'gemeente_akkoord']] = False

# Yorrid shit
gdf = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(df['locatie_longitude'], df['locatie_latitude']))
gdf = gdf.set_crs('EPSG:4326')

gebieden = gpd.read_file('/ext/MDS_2023-1_hackathon/groep_01/BestuurlijkeGebieden_2023.gml')
gebieden = gebieden.to_crs('EPSG:4326')
prov = gebieden.dissolve(by = 'ligtInProvincieNaam')
prov = prov.reset_index()[['ligtInProvincieNaam','geometry']]
gdf = gdf.sjoin(prov, predicate = 'within')

gdf.rename(columns = {'ligtInProvincieNaam':'provincie'}, inplace = True)

doorlooptijd_df = gdf[['tijdstip_aanvraag_netaansluiting', 'tijdstip_locatie_voorbereiden', 
                       'tijdstip_in_bedrijf', 'tijdstip_realisatie_plannen', 'tijdstip_accepteren_mra-e',
                       'provincie', 'locatie_latitude', 'locatie_longitude']].copy()

doorlooptijd_df = doorlooptijd_df.loc[(doorlooptijd_df['tijdstip_locatie_voorbereiden'].notna())]

doorlooptijd_df['aanvraag_voorbereiding'] = (doorlooptijd_df['tijdstip_realisatie_plannen'] - doorlooptijd_df['tijdstip_aanvraag_netaansluiting'])
doorlooptijd_df['voorbereiding_overdracht'] = (doorlooptijd_df['tijdstip_locatie_voorbereiden'] - doorlooptijd_df['tijdstip_accepteren_mra-e'])
doorlooptijd_df['ontvangst_oplevering'] = (doorlooptijd_df['tijdstip_in_bedrijf'] - doorlooptijd_df['tijdstip_accepteren_mra-e'])
doorlooptijd_df['aanvraag_oplevering'] = (doorlooptijd_df['tijdstip_in_bedrijf'] - doorlooptijd_df['tijdstip_aanvraag_netaansluiting'])

doorlooptijd = [doorlooptijd_df['aanvraag_voorbereiding'], doorlooptijd_df['voorbereiding_overdracht'], 
             doorlooptijd_df['ontvangst_oplevering'], doorlooptijd_df['aanvraag_oplevering']]

aanvragen = df.loc[(df['tijdstip_aangemaakt'].notna())]
loc_beoordeling = df.loc[(df['tijdstip_controle_locatievoorstel'].notna())]
advies_exp = df.loc[(df['tijdstip_advies_exploitant'].notna())]
verkeersbesluit = df.loc[(df['tijdstip_definitief_verkeersbesluit'].notna())]
goedkeuring_mra_e = df.loc[(df['tijdstip_accepteren_mra-e'].notna())]
netaansluiting = df.loc[(df['tijdstip_aanvraag_netaansluiting'].notna())]
laadpaal_oplevering = df.loc[(df['tijdstip_opleveren_laadpaal'].notna())]
locatie_oplevering = df.loc[(df['tijdstip_opleveren_locatie'].notna())]

# Convert to days
seconds_in_day = 86400
for i in range(len(doorlooptijd)):
    doorlooptijd[i] = doorlooptijd[i].dt.total_seconds() / seconds_in_day

doorlooptijd_in_dagen = pd.DataFrame(doorlooptijd).T
doorlooptijd_in_dagen.loc[(doorlooptijd_in_dagen['aanvraag_voorbereiding'] == 0), 'aanvraag_voorbereiding'] = None
doorlooptijd_in_dagen.dropna(inplace = True)

# Drop rows that have 0 days in any of the columns
doorlooptijd_in_dagen = doorlooptijd_in_dagen.loc[(doorlooptijd_in_dagen['aanvraag_voorbereiding'] > 0)]
doorlooptijd_in_dagen['provincie'] = doorlooptijd_df['provincie'] 

eleknet = gpd.read_file('/ext/MDS_2023-1_hackathon/groep_01/beschikbare_capaciteit_elektriciteitsnet.gpkg')
eleknet = eleknet.to_crs('EPSG:4326')
eleknet = eleknet.dropna()

# Figures
m = folium.Map(location=[52.558069, 5.171513], zoom_start=9, zoom_control=False)

folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_totaal'],
    key_on='feature.properties.pc4_code',
    name='Totaal',
    overlay=True,
    control=True,
    show=True,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Totale tijd (dagen)',
    highlight=True).add_to(m)
folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_a_b'],
    key_on='feature.properties.pc4_code',
    name='Aanvraagtijd',
    overlay=True,
    control=True,
    show=False,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Aanvraagtijd (dagen)',
    highlight=True).add_to(m)
folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_b_c'],
    key_on='feature.properties.pc4_code',
    name='Beoordelingstijd',
    overlay=True,
    control=True,
    show=False,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Beoordelingstijd (dagen)',
    highlight=True).add_to(m)
folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_c_d'],
    key_on='feature.properties.pc4_code',
    name='Besluittijd',
    overlay=True,
    control=True,
    show=False,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Besluittijd (dagen)',
    highlight=True).add_to(m)
folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_d_e'],
    key_on='feature.properties.pc4_code',
    name='Aannametijd',
    overlay=True,
    control=True,
    show=False,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Aannametijd (dagen)',
    highlight=True).add_to(m)
folium.Choropleth(
    geo_data = geofile,
    data=tijd_per_pc,
    columns=['postcode', 'tijd_e_f'],
    key_on='feature.properties.pc4_code',
    name='Realisatietijd',
    overlay=True,
    control=True,
    show=False,
    fill_color='YlOrRd',
    nan_fill_opacity=0,
    legend_name='Realisatietijd (dagen)',
    highlight=True).add_to(m)

folium.LayerControl('bottomleft').add_to(m)

# Distplot that shows the full lead time of the full process and the subprocesses
hist_data = [doorlooptijd_in_dagen['aanvraag_voorbereiding'], doorlooptijd_in_dagen['voorbereiding_overdracht'], 
             doorlooptijd_in_dagen['ontvangst_oplevering'], doorlooptijd_in_dagen['aanvraag_oplevering']]
labels = ['aanvraag - voorbereiding', 'voorbereiding - overdracht', 'ontvangst - oplevering', 'aanvraag - oplevering']

dist = ff.create_distplot(hist_data=hist_data, group_labels=labels, bin_size=1, show_rug=False, show_hist=False, show_curve=True, 
                         colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
dist.update_layout(title='Doorlooptijd', xaxis_title='Dagen', yaxis_title='Frequentie', legend_title='Aanvragen', font=dict(size=12),
                  xaxis=dict(rangeslider={'visible': True}))

# Scatter ternary plot for all the subprocesses and size based on the full proces time
ternary = px.scatter_ternary(doorlooptijd_in_dagen, a="ontvangst_oplevering", b="voorbereiding_overdracht", c="aanvraag_voorbereiding", 
                         color="provincie",size='aanvraag_oplevering', size_max=15, opacity=0.8, height=600, width=800)
ternary.update_layout(title='Doorlooptijd', legend_title='Provincie', font=dict(size=12))

# Bar chart Sidney
bar = go.Figure()

bar.add_trace(go.Histogram(x=aanvragen.tijdstip_aangemaakt,name = 'Aanvragen'))
bar.add_trace(go.Histogram(x=loc_beoordeling.tijdstip_aangemaakt,name = 'Locatie Beoordeling'))
bar.add_trace(go.Histogram(x=advies_exp.tijdstip_aangemaakt,name = 'Advies Exploitant'))
bar.add_trace(go.Histogram(x=verkeersbesluit.tijdstip_aangemaakt,name = 'Definitief Verkeersbesluit'))
bar.add_trace(go.Histogram(x=goedkeuring_mra_e.tijdstip_aangemaakt,name = 'Goedkeuring MRA-e'))
bar.add_trace(go.Histogram(x=netaansluiting.tijdstip_aangemaakt,name = 'Aanvraag Netaansluiting'))
bar.add_trace(go.Histogram(x=laadpaal_oplevering.tijdstip_aangemaakt,name = 'Oplevering Laadpaal'))
bar.add_trace(go.Histogram(x=locatie_oplevering.tijdstip_aangemaakt,name = 'Oplevering Locatie'))

bar.update_layout(legend_title_text = "Proces deel", xaxis={'rangeslider':{'visible':True}})
bar.update_xaxes(title_text="Tijd")
bar.update_yaxes(title_text="Aantal aanvragen")

# Streamlit initialization
st.set_page_config(layout='wide')
st.title('Evaluatie van laadpaal leveringen.')
col1, col2 = st.columns(2)
with col1:
    st.header('Choropleth van doorlooptijden')
    st.markdown('Hieronder wordt een choropleth weergegeven van doorlooptijden per postcode. Hierin zijn vier verschillende doorlooptijden te zien. De eerste weergeeft de doorlooptijd van de datum van aanvraag tot het begin van de locatie beoordeling. Ten tweede wordt de doorlooptijd van de locatie beoordeling van begin tot eind getoond. Ten derde wordt de tijd van eerste verkeersbesluit tot definitief besluit weergegeven. Als laatste is de totale doorlooptijd te zien.')
    folium_static(m, 875, 800)
    st.plotly_chart(bar, True)
with col2:
    st.plotly_chart(dist, True)
    st.plotly_chart(ternary, True)
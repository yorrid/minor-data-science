# %%
import pandas as pd
import numpy as np
import folium
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import datetime
import requests
import geopandas as gpd
from datetime import timedelta

# %%
df = pd.read_csv("Locatievoorstellen.csv", header=1, index_col=0)

# %%
pd.set_option("display.max_columns", None)

# %%
df.columns = df.columns.str.replace(" - ", "_")
df.columns = df.columns.str.replace(" ", "_")
df.columns = df.columns.str.lower()

# %%
df["tijdstip_van_laatste_wijziging"] = pd.to_datetime(
    df["tijdstip_van_laatste_wijziging"]
)
df["tijdstip_aangemaakt"] = pd.to_datetime(df["tijdstip_aangemaakt"])
df["tijdstip_locatievoorstel"] = pd.to_datetime(df["tijdstip_locatievoorstel"])
df["tijdstip_controle_locatievoorstel"] = pd.to_datetime(
    df["tijdstip_controle_locatievoorstel"]
)
df["tijdstip_advies_exploitant"] = pd.to_datetime(df["tijdstip_advies_exploitant"])
df["tijdstip_publicatie_verkeersbesluit"] = pd.to_datetime(
    df["tijdstip_publicatie_verkeersbesluit"]
)
df["tijdstip_aanvraag_netaansluiting"] = pd.to_datetime(
    df["tijdstip_aanvraag_netaansluiting"]
)
df["tijdstip_definitief_verkeersbesluit"] = pd.to_datetime(
    df["tijdstip_definitief_verkeersbesluit"]
)
df["tijdstip_accepteren_mra-e"] = pd.to_datetime(df["tijdstip_accepteren_mra-e"])
df["tijdstip_realisatie_plannen"] = pd.to_datetime(df["tijdstip_realisatie_plannen"])
df["tijdstip_locatie_voorbereiden"] = pd.to_datetime(
    df["tijdstip_locatie_voorbereiden"]
)
df["tijdstip_in_bedrijf"] = pd.to_datetime(df["tijdstip_in_bedrijf"])
df["tijdstip_opleveren_laadpaal"] = pd.to_datetime(df["tijdstip_opleveren_laadpaal"])
df["tijdstip_opleveren_locatie"] = pd.to_datetime(df["tijdstip_opleveren_locatie"])

# %%
df["doorlooptijd_d"] = df["tijdstip_opleveren_locatie"] - df["tijdstip_aangemaakt"]

# %%
df = df.drop(
    columns=[
        "stilgezet_uitleg",
        "verplaatsing_mra-e_laadpaal_id",
        "opmerkingen",
        "toelichting_bij_verplaatsing",
        "locatiecode",
        "aanbodgestuurd_opmerkingen",
        "datagestuurd_opmerkingen",
        "gemeente_akkoord_met_offerte_verplaatsing",
        "extra_laadpaal_ids",
        "referenties",
        "aanleiding",
    ]
)

# %%
df["postcode"] = df["postcode"].str.replace("[a-zA-Z]", "", regex=True)
df["postcode"] = df["postcode"].str.replace(" ", "", regex=True)

# %%
df.loc[
    (df["stilgezet"] == False) & df["doorlooptijd_d"].notna(),
    ["exploitant_akkoord", "aannemer_akkoord", "gemeente_akkoord"],
] = True
df.loc[
    (df["stilgezet"] == True) | df["doorlooptijd_d"].isna(),
    ["exploitant_akkoord", "aannemer_akkoord", "gemeente_akkoord"],
] = False

# %%
df["datum_oplevering_y"] = pd.DatetimeIndex(df["datum_oplevering"]).year
df["datum_oplevering_y"] = df["datum_oplevering_y"].fillna(0).astype(int)
df.loc[(df["datum_oplevering_y"] == 0), "datum_oplevering_y"] = None

# %%
df = df.loc[(df["datum_oplevering_y"] < 2024)]

# %%
gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df["locatie_longitude"], df["locatie_latitude"])
)
gdf = gdf.set_crs("EPSG:4326")

# %%
gebieden = gpd.read_file("BestuurlijkeGebieden_2023.gml")
gebieden = gebieden.to_crs("EPSG:4326")
prov = gebieden.dissolve(by="ligtInProvincieNaam")
prov = prov.reset_index()[["ligtInProvincieNaam", "geometry"]]
gdf = gdf.sjoin(prov, predicate="within")

# %%
gdf.rename(columns={"ligtInProvincieNaam": "provincie"}, inplace=True)

# %%
doorlooptijd_df = gdf[
    [
        "tijdstip_aanvraag_netaansluiting",
        "tijdstip_locatie_voorbereiden",
        "tijdstip_in_bedrijf",
        "tijdstip_realisatie_plannen",
        "tijdstip_accepteren_mra-e",
        "provincie",
        "locatie_latitude",
        "locatie_longitude",
    ]
].copy()

# %%
doorlooptijd_df = doorlooptijd_df.loc[
    (doorlooptijd_df["tijdstip_locatie_voorbereiden"].notna())
]

# %%
doorlooptijd_df["aanvraag_voorbereiding"] = (
    doorlooptijd_df["tijdstip_realisatie_plannen"]
    - doorlooptijd_df["tijdstip_aanvraag_netaansluiting"]
)
doorlooptijd_df["voorbereiding_overdracht"] = (
    doorlooptijd_df["tijdstip_locatie_voorbereiden"]
    - doorlooptijd_df["tijdstip_accepteren_mra-e"]
)
doorlooptijd_df["ontvangst_oplevering"] = (
    doorlooptijd_df["tijdstip_in_bedrijf"]
    - doorlooptijd_df["tijdstip_accepteren_mra-e"]
)
doorlooptijd_df["aanvraag_oplevering"] = (
    doorlooptijd_df["tijdstip_in_bedrijf"]
    - doorlooptijd_df["tijdstip_aanvraag_netaansluiting"]
)

# %%
doorlooptijd = [
    doorlooptijd_df["aanvraag_voorbereiding"],
    doorlooptijd_df["voorbereiding_overdracht"],
    doorlooptijd_df["ontvangst_oplevering"],
    doorlooptijd_df["aanvraag_oplevering"],
]


# %%
# Convert to days
seconds_in_day = 86400
for i in range(len(doorlooptijd)):
    doorlooptijd[i] = doorlooptijd[i].dt.total_seconds() / seconds_in_day

# %%
doorlooptijd_in_dagen = pd.DataFrame(doorlooptijd).T

# %%
doorlooptijd_in_dagen.loc[
    (doorlooptijd_in_dagen["aanvraag_voorbereiding"] == 0), "aanvraag_voorbereiding"
] = None
doorlooptijd_in_dagen.dropna(inplace=True)

# %%
# Drop rows that have 0 days in any of the columns
doorlooptijd_in_dagen = doorlooptijd_in_dagen.loc[
    (doorlooptijd_in_dagen["aanvraag_voorbereiding"] > 0)
]

# %%
doorlooptijd_in_dagen.eq(0).any().any()

# %%
doorlooptijd_in_dagen["provincie"] = doorlooptijd_df["provincie"]

# %% [markdown]
# Plotting

# %%
hist_data = [
    doorlooptijd_in_dagen["aanvraag_voorbereiding"],
    doorlooptijd_in_dagen["voorbereiding_overdracht"],
    doorlooptijd_in_dagen["ontvangst_oplevering"],
    doorlooptijd_in_dagen["aanvraag_oplevering"],
]
labels = [
    "aanvraag - voorbereiding",
    "voorbereiding - overdracht",
    "ontvangst - oplevering",
    "aanvraag - oplevering",
]

fig = ff.create_distplot(
    hist_data=hist_data,
    group_labels=labels,
    bin_size=1,
    show_rug=False,
    show_hist=False,
    show_curve=True,
    colors=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
)
fig.update_layout(
    title="Doorlooptijd",
    xaxis_title="Dagen",
    yaxis_title="Frequentie",
    legend_title="Aanvragen",
    font=dict(size=12),
    xaxis=dict(rangeslider={"visible": True}),
)
fig.show()

# %%
fig = px.scatter_ternary(
    doorlooptijd_in_dagen,
    a="ontvangst_oplevering",
    b="voorbereiding_overdracht",
    c="aanvraag_voorbereiding",
    color="provincie",
    size="aanvraag_oplevering",
    size_max=15,
    opacity=0.8,
    height=600,
    width=800,
)
fig.update_layout(
    title="Doorlooptijd",
    legend_title="Provincie",
    font=dict(size=12),
    labels=dict(
        a="ontvangst - oplevering",
    ),
)
fig.show()

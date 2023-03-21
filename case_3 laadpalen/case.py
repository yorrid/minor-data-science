import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import branca

#rdw dataset
# r = requests.get('https://opendata.rdw.nl/resource/8jni-y848.json')
r = requests.get('https://opendata.rdw.nl/resource/8wbe-pu7d.json')
rdw = pd.json_normalize(r.json())

#laadpaaldata
lpd = pd.read_csv('laadpaaldata.csv')

#opencharge dataset
response = requests.get('https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&maxresults=10000&compact=true&verbose=false&key=772ba88b-50db-49f1-b9f1-933c6053edd3')

json_lp = response.json()

opencharge = pd.json_normalize(json_lp)

df4 = pd.json_normalize(opencharge.Connections)
df5 = pd.json_normalize(df4[0])

ocm = pd.concat([opencharge, df5], axis=1)

ocm.columns = ocm.columns.str.replace('.', '_') 
ocm.columns = ocm.columns.str.replace(' ', '_')

ocm = ocm.loc[:,~ocm.columns.duplicated()].copy()
ocm = ocm[ocm['Quantity'].notna()]
ocm = ocm[ocm['NumberOfPoints'] != 0]
ocm = ocm[ocm['AddressInfo_Latitude'] > 50]
ocm = ocm.drop(columns=['Connections','AddressInfo_DistanceUnit', 'GeneralComments', 'AddressInfo_RelatedURL', 'UsageCost', 'AddressInfo_AddressLine2', 'AddressInfo_AccessComments', 
                        'AddressInfo_ContactTelephone1', 'AddressInfo_ContactEmail', 'AddressInfo_ContactTelephone2', 'OperatorsReference', 'DataProvidersReference',
                        'MetadataValues', 'DateLastConfirmed', 'Reference', 'Amps', 'Voltage', 'Comments'])
ocm.columns = map(str.lower, ocm.columns)
rdw.columns = map(str.lower, rdw.columns)
lpd.columns = map(str.lower, lpd.columns)

ocm['addressinfo_postcode'] = ocm['addressinfo_postcode'].str.replace('[a-zA-Z]', '')
ocm['addressinfo_postcode'] = ocm['addressinfo_postcode'].str.replace(' ', '')

# Folium mapping functions
def folium_static(fig,width=700, height=500,colors=['#5e4fa2', '#89d0a4', '#fffebe', '#f88c51', '#9e0142'],
                  labels=['Muito Baixo', 'Baixo', 'Médio', 'Médio - Alto', 'Alto'], title='Criticidade'):

    # if Map, wrap in Figure
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)
        fig = add_categorical_legend(fig, title,
                                         colors=colors,
                                         labels=labels)
        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
        )

    # if DualMap, get HTML representation
    elif isinstance(fig, folium.plugins.DualMap) or isinstance(
        fig, branca.element.Figure
    ):
        return components.html(fig._repr_html_(), height=height + 10, width=width)

def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))

    legend_categories = ""
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"

    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """

    css = """

    <style type='text/css'>
      .maplegend {
      position: relative;
      z-index:9999;
      border:2px solid grey;
      background-color:rgba(255, 255, 255, 0.8);
      border-radius:6px;
      padding: 10px;
      font-size:14px;
      right: 20px;
      top: 20px;
      float:right;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 18px;
        width: 18px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map


# Colorpicker function
def colorpicker(value):
    if value >= 300:
        return color[9]
    elif value >= 250:
        return color[8]
    elif value >= 200:
        return color[7]
    elif value >= 150:
        return color[6]
    elif value >= 100:
        return color[5]
    elif value >= 50:
        return color[4]
    elif value >= 25:
        return color[3]
    elif value >= 10:
        return color[2]
    elif value >= 5:
        return color[1]
    elif value >= 0:
        return color[0]



# Streamlit initialisation
st.title('Laadpalen case')
st.header('RDW data')
st.dataframe(rdw)
st.header('Laadpaal data')
st.dataframe(lpd)
st.header('Open Charge Map data')
st.dataframe(ocm)
st.header('Spread of charging points and the power output')
area = st.selectbox('Select area to view', 
             ('Netherlands', 'Groningen', 'Friesland', 'Noord-Holland', 'Zuid-Holland', 'Utrecht', 'Flevoland', 'Drenthe', 'Overijssel',
               'Gelderland', 'Zeeland', 'Noord-Brabant', 'Limburg'), 0)

if area == 'Netherlands':
    location = [52.091684, 5.114055]
    zoom = 7
elif area == 'Groningen':
    location = [53.152072, 6.791522]
    zoom = 9
elif area == 'Friesland':
    location = [53.093875, 5.892489]
    zoom = 9
elif area == 'Noord-Holland':
    location = [52.595233, 4.873177]
    zoom = 9
elif area == 'Zuid-Holland':
    location = [52.023114, 4.533930]
    zoom = 9
elif area == 'Utrecht':
    location = [52.089617, 5.159590]
    zoom = 10
elif area == 'Flevoland':
    location = [52.480259, 5.574270]
    zoom = 9
elif area == 'Drenthe':
    location = [52.902488, 6.623687]
    zoom = 9
elif area == 'Overijssel':
    location = [52.425587, 6.473226]
    zoom = 9
elif area == 'Gelderland':
    location = [52.007641, 5.899189]
    zoom = 9
elif area == 'Zeeland':
    location = [51.514950, 3.990977]
    zoom = 9
elif area == 'Noord-Brabant':
    location = [51.562279, 5.225843]
    zoom = 9
elif area == 'Limburg':
    location = [51.104646, 5.924995]
    zoom = 9    

# Folium map
m = folium.Map(location=location, zoom_start=zoom, tiles='CartoDB positron')

color = ["#9E0142", "#D53E4F", "#F46D43", "#FDAE61", "#FEE08B", "#E6F598", "#ABDDA4", "#66C2A5", "#3288BD", "#5E4FA2"]
label = ['0-4 kW', '5-9 kW', '10-24 kW', '25-49 kW', '50-99 kW', '100-149 kW', '150-199 kW', '200-249 kW', '250-299 kW', '300 or greater kW']

for i, row in ocm.iterrows():
    folium.Circle(location=[row['addressinfo_latitude'], row['addressinfo_longitude']], 
                  fill=True, fill_opacity=0.7, radius=60*zoom, popup=row['addressinfo_title'], 
                  color=colorpicker(row['powerkw'])).add_to(m)
folium_static(m, colors=color, labels=label, title='Power output')
import pandas as pd
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
import branca
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

#rdw dataset
rdw = pd.read_csv('fuel_count.csv')
rdw.rename({'datum_eerste_toelating':'date_of_acceptance','benzine_count': 'gasoline_count', 'elektriciteit_count':'electric_count', 'waterstof_count':'hydrogen_count'}, inplace=True, axis=1)

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

lpd = lpd.loc[(lpd['chargetime'] >= 0)]

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

# Cumulative line graph
cum_fuel = go.Figure(layout_yaxis_range=[0,8])
columns = rdw.columns[1:]

for column in columns:
    cum_fuel.add_trace(go.Scatter(x=rdw['date_of_acceptance'], y=rdw[column], name=column.split('_')[0].title()))

cum_fuel_dropdown = [ {'label': 'All', 'method': 'update','args': [{'visible': [True, True, True, True, True, True, True, True]}, {'title': 'Cumulative sum of vehicles per fuel type over time'}]},
                      {'label': 'Gasoline', 'method': 'update','args': [{'visible': [True, False, False, False, False, False, False, False]},     {'title': 'Cumulative sum of gasoline vehicles over time'}]},  
                      {'label': 'Electric', 'method': 'update','args': [{'visible': [False, True, False, False, False, False, False, False]}, {'title': 'Cumulative sum of electric vehicles over time'}]},  
                      {'label': 'Diesel', 'method': "update",'args': [{"visible": [False, False, True, False, False, False, False, False]},   {'title': 'Cumulative sum of diesel vehicles over time'}]},
                      {'label': 'Hydrogen', 'method': "update",'args': [{"visible": [False, False, False, True, False, False, False, False]},   {'title': 'Cumulative sum of hydrogen vehicles over time'}]},
                      {'label': 'Alcohol', 'method': "update",'args': [{"visible": [False, False, False, False, True, False, False, False]},   {'title': 'Cumulative sum of alcohol vehicles over time'}]},
                      {'label': 'LPG', 'method': "update",'args': [{"visible": [False, False, False, False, False, True, False, False]},   {'title': 'Cumulative sum of LPG vehicles over time'}]},
                      {'label': 'CNG', 'method': "update",'args': [{"visible": [False, False, False, False, False, False, True, False]},   {'title': 'Cumulative sum of CNG vehicles over time'}]},
                      {'label': 'LNG', 'method': "update",'args': [{"visible": [False, False, False, False, False, False, False, True]},   {'title': 'Cumulative sum of LNG vehicles over time'}]}]

cum_fuel.update_layout(legend={'title':'Fuel type'}, title={'text':'Cumulative sum of vehicles per fuel type over time'}, xaxis={'rangeslider':{'visible':True}},
                       updatemenus=[{'type': "dropdown",'x': 1.15, 'y': 0,'showactive': True,'active': 0,'buttons': cum_fuel_dropdown}])
cum_fuel.update_xaxes(patch={'title':'Date'})
cum_fuel.update_yaxes(patch={'title':'Amount of vehicles'}, type='log')

# Streamlit initialisation
st.set_page_config(layout='wide', page_title='Electric driving in the Netherlands')
st.title('Electric driving in the Netherlands')

col1, col2 = st.columns(2)
with col1:

    st.markdown('This dashboard aims to show the transition from fuel type used in vehicles in the Netherlands. It will show the counts of vehicles of each fuel type going back to 1877. Furthermore, the percentage of electric vehicles and the expected increase in percentage over time will be explored. Electric vehicles need accommodations for charging. This is shown in a map of charging locations in the Netherlands. Charging behaviour is also shown to give an indication of what is expected from the charging stations.')
    # Vehicles per fuel type over time plot
    st.header('Amounts of vehicles per fuel type over time')
    st.markdown('This chart shows the progression in the amount of vehicles per fuel type. This data has been obtained from two RDW datasets that have been merged to create the visualisation. In total, roughly 14 million vehicles have registered going back to 1877 till present day. The graph contains a logarythmic y-axis that shows that gasoline powered vehicles are still most prevalent current day with diesel vehicles second and electric third. In the last 20 years, the number of electric vehicles has grown exponentially.')
    st.plotly_chart(cum_fuel, True)

    st.header('Change in percentage of electric vehicles over time')
    left1, left2 = st.columns([3, 1])
    # Ratio of electric to non electric vehicles plot
        # Radio buttons
    with left1:
        st.markdown('This graph shows the percentage of electric vehicles of all vehicles since 2010. Currently, electric vehicles make up roughly 10 percent of all vehicles in the netherlands, from the regression line it is also visible that this exponential increase is still continues. This reflects the climate change acts that are enacted that place focus on increasing the amount of green electric vehicles and the reduction of fossil fuel vehicles.')

    with left2:
        check = st.radio('Standard or logarythmic y-axis', ['Standard', 'Logarythmic'])
        if check == 'Standard':
            type = '-'
        else:
            type = 'log'
    
        # Chart
    rdw['date_of_acceptance'] = rdw['date_of_acceptance'].astype('datetime64[ns]')

    rdw['non_electric'] = rdw['gasoline_count'] + rdw['diesel_count'] + rdw['hydrogen_count'] + rdw['alcohol_count'] + \
        rdw['lpg_count'] + rdw['cng_count'] + rdw['lng_count']
    
    rdw['ratio_electric'] = (rdw['electric_count'] / rdw['non_electric']) * 100

    time_filter = rdw.loc[(rdw['date_of_acceptance'] > '2010-01-01')]

    scatter = px.scatter(time_filter, x='date_of_acceptance', y='ratio_electric', trendline='ols', trendline_options=dict(log_y=True),
                          trendline_color_override='red', title='Percentage of electric vehicles over time')
    scatter.update_yaxes(type=type)
    scatter.update_xaxes(patch={'title':'Date'})
    scatter.update_yaxes(patch={'title':'Percentage electric vehicles of total amount'})
    st.plotly_chart(scatter, True)
    
    rdw['date_of_acceptance'] = rdw['date_of_acceptance'].astype('datetime64[ns]')

    rdw['electric'] = rdw['electric_count']

    rdw['non_electric'] = rdw['gasoline_count'] + rdw['diesel_count'] + rdw['hydrogen_count'] + rdw['alcohol_count'] + rdw['lpg_count'] + rdw['cng_count'] + rdw['lng_count']
        
    rdw['electric_percentage'] = (rdw['electric'] / (rdw['electric'] + rdw['non_electric']) * 100)

    rdw = rdw[rdw['date_of_acceptance'] >= '2010-01-01']
    rdw = rdw[rdw['date_of_acceptance'] <= '2022-12-31']
    input1 = rdw['electric'].to_list()
    X1 = rdw['date_of_acceptance']
    y1 = np.log10(input1)

    model = LinearRegression()
    model.fit(X1.values.reshape(-1,1), y1)

    X_predict1 = pd.date_range(start='2023-01-01', end='2051-01-01', freq='MS')
    y_predict1 = model.predict(X_predict1.values.reshape(-1,1).astype("float64"))
    new_electric = 10**(y_predict1)
    df = pd.DataFrame()
    df['pre_electric'] = new_electric.tolist()
    input2 = rdw['non_electric'].to_list()
    X2 = rdw['date_of_acceptance']
    y2 = np.log10(input2)

    model = LinearRegression()
    model.fit(X2.values.reshape(-1,1), y2)

    X_predict2 = pd.date_range(start='2023-01-01', end='2051-01-01', freq='MS')
    y_predict2 = model.predict(X_predict2.values.reshape(-1,1).astype("float64"))
    new_non_electric = 10**(y_predict2)
    df['pre_non_electric'] = new_non_electric.tolist()
    df['percentage'] = (df['pre_electric'] / (df['pre_electric'] + df['pre_non_electric']) * 100)
    df['date'] = X_predict2
    prediction_plot = px.line(x = df.date, y = df.percentage, title='Predicted growth of the percentage of electric vehicles over time.', labels={'y': 'Percentage of electric vehicles', 'x': 'Date'})
    
    st.markdown('Below is the predictive plot of the percentage of electric vehicles in relation to all vehicles. This shows that over time, it is expected that electric vehicles will become the large majority of vehicles. This has been deduced using a linear regression algorythm from Scikit learn.')
    st.plotly_chart(prediction_plot, True)

with col2:
    st.header('Spread of charging points and the power output')
    st.markdown('This map shows the location of all charging points in the Netherlands found on Open Charge Map. Each charging point has been given a colour based on the maximum power output that is available at that location. Furthermore, its address and number of charging points is shown on-click. The map can be recentered on all the Dutch provinces and charging points can be filtered based on the desired minimum and maximum power output.')
    # Folium map plot
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

    sld1, sld2 = st.columns(2)
    with sld1:
        min_slider = st.slider('Select minimum power output', 0, 350, 0)
    with sld2: 
        max_slider = st.slider('Select maximum power output', min_slider, 350, 350)
    ocm = ocm[(ocm['powerkw'] >= min_slider) & (ocm['powerkw'] <= max_slider)]

    # Folium map
    m = folium.Map(location=location, zoom_start=zoom, tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', attr='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community', 
                min_zoom=zoom, prefer_canvas=True)

    color = ["#9E0142", "#D53E4F", "#F46D43", "#FDAE61", "#FEE08B", "#E6F598", "#ABDDA4", "#66C2A5", "#3288BD", "#5E4FA2"]
    label = ['0-4 kW', '5-9 kW', '10-24 kW', '25-49 kW', '50-99 kW', '100-149 kW', '150-199 kW', '200-249 kW', '250-299 kW', '300 or greater kW']

    for i, row in ocm.iterrows():
        folium.Circle(location=[row['addressinfo_latitude'], row['addressinfo_longitude']], 
                    fill=True, fill_opacity=0.7, radius=60*zoom, 
                    popup='<b>Addres:</b> '+row['addressinfo_title']+',\n<b>Power output:</b> '+str(row['powerkw'])+ ' kW,\n<b>Number of charging points:</b> '+str(round(row['numberofpoints'])), 
                    tooltip='Click to see more details', color=colorpicker(row['powerkw'])).add_to(m)
    folium_static(m, colors=color, labels=label, title='Power output', width=850)

    #Charge time plot
    con_time_hist = lpd.loc[(lpd['connectedtime'] < 20)]
    chr_time_hist = lpd.loc[(lpd['chargetime'] < 20)]

    hist_data = [chr_time_hist['chargetime'], con_time_hist['connectedtime']]
    group_labels = ['Charge Time', 'Connected Time']

    cht_avg = round(lpd['chargetime'].mean(), 2)
    cht_median = round(lpd['chargetime'].median(), 2)
    ct_avg = round(lpd['connectedtime'].mean(), 2)
    ct_median = round(lpd['connectedtime'].median(), 2)

    fig = ff.create_distplot(hist_data, group_labels, bin_size=[.1, .25, .5, 1], show_rug=False)
    fig.update_layout({'title': {'text': 'Probability distribution of charging & connected time'}}, xaxis=dict(rangeslider={'visible': True}))
    fig.update_xaxes(patch={'title':'Time (hours)'})
    fig.update_yaxes(patch={'title':'Probability density'})
    fig.add_annotation(x=15, y=0.8,
                text=f"Average charge time: {cht_avg} hours",
                showarrow=False,
                yshift=10)
    fig.add_annotation(x=15, y=0.7,
                text=f"Median charge time: {cht_median} hours",
                showarrow=False,
                yshift=10)
    fig.add_annotation(x=15, y=0.5,
                text=f"Average connected time: {ct_avg} hours",
                showarrow=False,
                yshift=10)
    fig.add_annotation(x=15, y=0.4,
                text=f"Median connected time: {ct_median} hours",
                showarrow=False,
                yshift=10)
    st.header('Time connected and charge time distribution')
    st.markdown('This graph shows the spread of times that electric vehicles are connected and the required charging times. A histogram shows the amount of observations in the bins with a probability density line graph over it to show the probability density per value. Annotations show the mean and median values of both charge times and connected times. Connected times contain a large number of long times, this is explained by the fact that some owners leave their vehicle connected for longer durations when the vehicle is not in use. Charge times are spread mostly evenly between 0 and 4 hours, which is explained by the fact that the power output of charging ports changes from port to port. This increases charging time when the vehicle receives less power. ')
    st.plotly_chart(fig, True)
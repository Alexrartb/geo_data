import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import streamlit as st
from streamlit_folium import folium_static


def set_points(lat_series, lon_series, name_series, world_map):
    for lat, lon, name in zip(lat_series, lon_series, name_series):
        folium.Marker([lat, lon],
                      radius=10,
                      popup=('<strong>name</strong>: ' + str(name).capitalize() + '<br>'
                             ),
                      fill_opacity=0.7).add_to(world_map)
    return world_map

def draw_arrow(world_map, df):
    for item in df[['lat_from', 'lon_from', 'lat_to', 'lon_to']].values:
        coordinates = [(item[0], item[1]), (item[2], item[3])]
        aline = folium.PolyLine(locations=coordinates,
                                weight=2,
                                color='darkblue'
                                )
        world_map.add_child(aline)
        #         рисование стрелки
        folium.RegularPolygonMarker(location=coordinates[1],
                                    fill_color='darkblue',
                                    number_of_sides=3,
                                    radius=10
                                    ).add_to(world_map)
    return world_map

def draw_map(df):
    world_map = folium.Map(location=[10, -20], zoom_start=2.3)
    #     нарисовать точки откуда
    world_map = set_points(df['lat_from'], df['lon_from'], df['load_port'], world_map)
    #     нарисовать точки куда
    world_map = set_points(df['lat_to'], df['lon_to'], df['disch_port'], world_map)
    #     нарисовать стрелки
    world_map = draw_arrow(world_map, df)
    return world_map

@st.cache(show_spinner=True)
def load_data(path):
    df = pd.read_excel(path, sheet_name='data')
    df.columns = df.columns.str.strip()
    # df['year'] = df['year'].astype('int')
    return df

@st.cache
def filter_df(filters_dict, df):
    # df = df.loc[(df['year'] <= year_to) & (df['year'] >= year_from)]
    for col in filters_dict.keys():
        if filters_dict[col]:
            df = df.loc[df[col].isin(filters_dict[col])]
    return df

path = r'geo_data.xlsx'
with st.spinner('Loading data...'):
    df = load_data(path)


# year_from = st.sidebar.slider('Choose period from (<=)', min_value = df['year'].min(), max_value=df['year'].max(), step=1)
# year_to = st.sidebar.slider('Choose period to (>=)', min_value = df['year'].min() + 1, max_value=df['year'].max(), step=1)

filters_dict = {
                'load_port':st.sidebar.multiselect('Choose load port',df['load_port'].unique()),
                'disch_port':st.sidebar.multiselect('Choose disch port',df['disch_port'].unique()),
                'commodity_name':st.sidebar.multiselect('Choose commodity name',df['commodity_name'].unique())
                }

df = filter_df(filters_dict, df)
st.write(df)

with st.spinner('Draw map...'):
    folium_static(draw_map(df))

x = st.selectbox('Y coordinate', ['commodity_name','load_port','disch_port'])
with st.spinner('Plot your chart...'):
    fig, ax = plt.subplots(figsize=(20,8))
    sns.set_theme(style="whitegrid")
    sns.barplot(data=df,
                y='voy_intake, tones',
                x=x,
                ax=ax
               )
    fig.autofmt_xdate()
    st.write(fig)

x_sec = st.selectbox('X coordinate', ['commodity_name','load_port','disch_port'])
with st.spinner('Plot your chart...'):
    fig, ax = plt.subplots(figsize=(20,8))
    sns.lineplot(y = 'voy_intake, tones',
            x = x_sec,
                 data = df.head(50), ax = ax
           )
    fig.autofmt_xdate()
    plt.legend(['voy_intake, tones'])
    st.write(fig)
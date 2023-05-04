# Bibliotecas necessárias para a construção da aplicação
import pandas as pd
import numpy as np
import streamlit as st
import folium
import geopandas
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


# Arquivos utilizados para a resolução do problema
data_raw = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/kc_house_data.csv'
geofile = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/Zip_Codes.geojson'

# Início da classe "Houserocket":
# Função para carregar e transformar os dados
def read_data():
    df = pd.read_csv(data_raw)
    df['bathrooms'] = np.int64(round(df['bathrooms'] - 0.3))
    df['floors'] = np.int64(round(df['floors'] - 0.3))
    df['waterfront'] = df['waterfront'].apply(lambda x: 'SIM' if x == 1 else 'NÃO')
    df['age'] = np.int64(np.int64(pd.to_datetime(df['date']).dt.strftime('%Y')) - df['yr_built'])
    df.drop(
        columns=['sqft_living', 'sqft_above', 'sqft_basement', 'yr_renovated', 'sqft_living15', 'sqft_lot15', 'date'],
        axis=1, inplace=True)
    dados_remove = []
    for c in range(0, len(df['bedrooms'])):
        if (df['bedrooms'][c] in [0, 7, 8, 9, 10, 11, 33]) | (df['bathrooms'][c] in [0, 7, 8]):
            dados_remove.append(c)

    df.drop(index=dados_remove, inplace=True)
    return df


# Função para construir o mapa
def load_map(data):
    data_map = geopandas.read_file(geofile)
    mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()])

    marker_cluster = MarkerCluster().add_to(mapa)
    for name, row in data.iterrows():
        folium.Marker(location=[row['lat'], row['long']], popup=f'''
        ID:{row["id"]}
        PREÇO:{row["price"]}
        BEIRA-MAR:{row["waterfront"]}
        BANHEIROS:{row["bathrooms"]}
        QUARTOS:{row["bedrooms"]}
        ''').add_to(marker_cluster)

    df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    data_map = data_map[data_map['ZIP'].isin(data['zipcode'].tolist())]
    folium.Choropleth(geo_data=data_map, data=df, columns=['zipcode', 'price'], key_on='feature.properties.ZIP',
                      fill_color='YlOrRd',
                      fill_opacity=0.9,
                      line_opacity=0.4).add_to(mapa)
    return folium_static(mapa)


# Carregando e transformando as variaveis
dataframe_st = read_data()

# sidebar
st.sidebar.title('Localização e atributos')
show_dataframe = st.sidebar.checkbox('Mostrar tabela', True)
show_map = st.sidebar.checkbox('Mostrar mapa')
filter_id = st.sidebar.multiselect('ID das casas', dataframe_st['id'].unique().tolist())
filter_price = st.sidebar.slider('Preço das casas', int(dataframe_st['price'].min()), int(dataframe_st['price'].max()),
                                 int(dataframe_st['price'].mean()))
filter_bedrooms = st.sidebar.selectbox('Número de quartos', dataframe_st['bedrooms'].sort_values().unique().tolist())
filter_bathrooms = st.sidebar.selectbox('Número de banheiros',
                                        dataframe_st['bathrooms'].sort_values().unique().tolist())
filter_waterfront = st.sidebar.selectbox('Beira-mar', dataframe_st['waterfront'].unique().tolist())

# Plotando no corpo central do aplicativo
if filter_id:
    dataframe_st = dataframe_st.loc[dataframe_st['id'].isin(filter_id)]
else:
    dataframe_st = dataframe_st.loc[(dataframe_st['price'] <= filter_price) &
                                    (dataframe_st['bedrooms'].isin([filter_bedrooms])) &
                                    (dataframe_st['bathrooms'].isin([filter_bathrooms])) &
                                    (dataframe_st['waterfront'].isin([filter_waterfront]))]

if show_dataframe:
    st.dataframe(dataframe_st)
    st.info(f'Total de {len(dataframe_st)} casas')

if (show_map == True) & (show_dataframe == True) & (len(dataframe_st) != 0):
    load_map(data=dataframe_st[['id', 'zipcode', 'lat', 'long', 'price', 'bedrooms', 'bathrooms', 'waterfront']])

if (show_map == True) & (show_dataframe == False) & (len(dataframe_st) != 0):
    st.info(f'Total de {len(dataframe_st)} casas')
    load_map(data=dataframe_st[['id', 'zipcode', 'lat', 'long', 'price', 'bedrooms', 'bathrooms', 'waterfront']])

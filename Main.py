# Bibliotecas necessárias para a construção da aplicação
import pandas as pd
import numpy as np
import streamlit as st
import folium
import geopandas
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster


class HouseRocket:
    def __init__(self, file, geojsonfile):
        self.file = pd.read_csv(file)
        self.geojsonfile = geopandas.read_file(geojsonfile)

    def data_processing(self):
        self.file['bathrooms'] = np.int64(round(self.file['bathrooms'] - 0.3))
        self.file['floors'] = np.int64(round(self.file['floors'] - 0.3))
        self.file['waterfront'] = self.file['waterfront'].apply(lambda x: 'SIM' if x == 1 else 'NÃO')
        self.file['age'] = np.int64(
            np.int64(pd.to_datetime(self.file['date']).dt.strftime('%Y')) - self.file['yr_built'])
        self.file.drop(
            columns=['sqft_living', 'sqft_above', 'sqft_basement', 'yr_renovated', 'sqft_living15', 'sqft_lot15',
                     'date'],
            axis=1, inplace=True)
        dados_remove = []
        for c in range(0, len(self.file['bedrooms'])):
            if (self.file['bedrooms'][c] in [0, 7, 8, 9, 10, 11, 33]) | (self.file['bathrooms'][c] in [0, 7, 8]):
                dados_remove.append(c)

        self.file.drop(index=dados_remove, inplace=True)
        return self.file

    def reading_map(self, datamap):
        mapa = folium.Map(location=[datamap['lat'].mean(), datamap['long'].mean()])

        marker_cluster = MarkerCluster().add_to(mapa)
        for name, row in datamap.iterrows():
            folium.Marker(location=[row['lat'], row['long']], popup=f'''
                ID:{row["id"]}
                PREÇO:{row["price"]}
                BEIRA-MAR:{row["waterfront"]}
                BANHEIROS:{row["bathrooms"]}
                QUARTOS:{row["bedrooms"]}
                ''').add_to(marker_cluster)

        df = datamap[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
        data_map = self.geojsonfile[self.geojsonfile['ZIP'].isin(datamap['zipcode'].tolist())]
        folium.Choropleth(geo_data=data_map, data=df, columns=['zipcode', 'price'], key_on='feature.properties.ZIP',
                          fill_color='YlOrRd',
                          fill_opacity=0.9,
                          line_opacity=0.4).add_to(mapa)
        return folium_static(mapa)


file_raw = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/kc_house_data.csv'
geofile = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/Zip_Codes.geojson'
houserocket = HouseRocket(file=file_raw, geojsonfile=geofile)
dataframe = houserocket.data_processing()
# sidebar
st.sidebar.title('Localização e atributos')
show_dataframe = st.sidebar.checkbox('Mostrar tabela', True)
show_map = st.sidebar.checkbox('Mostrar mapa')
filter_id = st.sidebar.multiselect('ID das casas', dataframe['id'].unique().tolist())
filter_price = st.sidebar.slider('Preço das casas', int(dataframe['price'].min()), int(dataframe['price'].max()),
                                 int(dataframe['price'].mean()))
filter_bedrooms = st.sidebar.selectbox('Número de quartos', dataframe['bedrooms'].sort_values().unique().tolist())
filter_bathrooms = st.sidebar.selectbox('Número de banheiros',
                                        dataframe['bathrooms'].sort_values().unique().tolist())
filter_waterfront = st.sidebar.selectbox('Beira-mar', dataframe['waterfront'].unique().tolist())

# Plotando no corpo central do aplicativo
if filter_id:
    dataframe_st = dataframe.loc[dataframe['id'].isin(filter_id)]
else:
    dataframe_st = dataframe.loc[(dataframe['price'] <= filter_price) &
                                 (dataframe['bedrooms'].isin([filter_bedrooms])) &
                                 (dataframe['bathrooms'].isin([filter_bathrooms])) &
                                 (dataframe['waterfront'].isin([filter_waterfront]))]

filter_map = dataframe_st[['id', 'zipcode', 'lat', 'long', 'price', 'bedrooms', 'bathrooms', 'waterfront']]

if (show_map == False) & (show_dataframe == True):
    st.dataframe(dataframe_st)
elif (show_map == True) & (show_dataframe == True) & (len(dataframe_st) != 0):
    st.dataframe(dataframe_st)
    houserocket.reading_map(datamap=filter_map)
elif (show_map == True) & (show_dataframe == False) & (len(dataframe_st) != 0):
    houserocket.reading_map(datamap=filter_map)

![house_rocket_img](https://user-images.githubusercontent.com/67663958/235933037-a6e78549-6ad2-4e37-a4ae-ba53fc8842b0.png)


# RESUMO
A House Rocket é uma plataforma digital que tem como modelo de negócio, a compra e a venda de imóveis usando tecnologia. A plataforma necessita de uma melhor forma para buscar boas oportunidades de compra de casas em Seattle.

# INTRODUÇÃO
 A aplicação possibilita a utilização de filtro para facilitar a busca de casas por meio do preço, número de banheiros, quartos e se é beira-mar para que essas casas sejam demonstradas em um mapa que divide as áreas por média de preço e mostra as informações de cada casa junto a uma tabela.

# SOLUÇÃO
Retirando os dados do kaggle (https://www.kaggle.com/shivachandel/kc-house-data), e importando no Jupyter Notebook para fazer a análise exploratória de dados, é possível criar insights para um melhor desenvolvimento da solução e descobrir dados que tendem a ser desnecessários para a aplicação. Aplicando a limpeza e transformação dos dados, que irão aprimorar o que necessitamos para resolver o problema, a partir do pycharm, e selecionando os melhores atributos, levando em conta o que é pedido, é possível construir um relatório utilizando mapa e filtros que sejam colocados em produção no Streamlit, assim, facilitando a tomada de decisão. Os dados retirados para a construção do mapa (https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::zip-codes/explore?location=47.243611%2C-121.083221%2C7.39).

**Código da solução:** https://bit.ly/44mtXQf

![2023-05-03-10-50-36](https://user-images.githubusercontent.com/67663958/235936276-3fa83d82-2a12-47a9-bf39-42f0509ffbb6.gif)


# FERRAMENTAS
Python 3.9.13

PyCharm Community Edition 2022.1.3

folium 0.12.1

geopandas 0.10.2

numpy 1.20.3

pandas 1.2.4

plotly 5.4.0

streamlit 1.5.1

streamlit-folium 0.5.0

# SOBRE O CÓDIGO
```python
# pandas foi utilizado para carregar o arquivo .csv
import pandas as pd
# numpy foi utilizado para transformação dos dados
import numpy as np
# Construir a aplicação web
import streamlit as st
# Criação do mapa
import folium
# Carregamento do arquivo .geojson
import geopandas
# Demonstração do mapa na aplicação web
from streamlit_folium import folium_static
# Acrescentação de pontos e informações no mapa
from folium.plugins import MarkerCluster
```

```python
# Arquivos utilizados para a construção da aplicação (ambos voltado para Seattle)
data_raw = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/kc_house_data.csv'
geofile = 'https://raw.githubusercontent.com/HedvaldoCosta/HouseRocket/main/Arquivos/Zip_Codes.geojson'
```

```python
# Função utilizada para carregar o arquivo da variável "data_raw" e tratar os dados
def read_data():
    df = pd.read_csv(data_raw)
    # Tratamento dos dados para arredondar os valores nas colunas
    # banheiros e andares. Não seria viável utilizar valores float 
    df['bathrooms'] = np.int64(round(df['bathrooms'] - 0.3))
    df['floors'] = np.int64(round(df['floors'] - 0.3))
    # Mudando os dados da coluna "waterfront" para uma melhor demonstração
    # no filtro "beira-mar" criado na aplicação
    df['waterfront'] = df['waterfront'].apply(lambda x: 'SIM' if x == 1 else 'NÃO')
    # Pegando apenas o ano de cada casa e aplicando em uma nova coluna
    df['age'] = np.int64(np.int64(pd.to_datetime(df['date']).dt.strftime('%Y')) - df['yr_built'])
    # Excluindo dados desnecessários para a criação da aplicação
    df.drop(
        columns=['sqft_living', 'sqft_above', 'sqft_basement', 'yr_renovated', 'sqft_living15', 'sqft_lot15', 'date'],
        axis=1, inplace=True)
    dados_remove = []
    # Excluindo outliers
    for c in range(0, len(df['bedrooms'])):
        if (df['bedrooms'][c] in [0, 7, 8, 9, 10, 11, 33]) | (df['bathrooms'][c] in [0, 7, 8]):
            dados_remove.append(c)

    df.drop(index=dados_remove, inplace=True)
    return df
```
```python
# Função utilizada para carregar o arquivo .geojson e aplicar marcação e 
# executar o mapa
def load_map(data):
    data_map = geopandas.read_file(geofile)
    # Pegando os dados de latitude e longitude para criar o mapa
    mapa = folium.Map(location=[data['lat'].mean(), data['long'].mean()])
    # Criação dos marcadores no mapa
    marker_cluster = MarkerCluster().add_to(mapa)
    for name, row in data.iterrows():
        folium.Marker(location=[row['lat'], row['long']], popup=f'''
        ID:{row["id"]}
        PREÇO:{row["price"]}
        BEIRA-MAR:{row["waterfront"]}
        BANHEIROS:{row["bathrooms"]}
        QUARTOS:{row["bedrooms"]}
        ''').add_to(marker_cluster)
    # Execução do mapa
    df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
    data_map = data_map[data_map['ZIP'].isin(data['zipcode'].tolist())]
    folium.Choropleth(geo_data=data_map, data=df, columns=['zipcode', 'price'], key_on='feature.properties.ZIP',
                      fill_color='YlOrRd',
                      fill_opacity=0.9,
                      line_opacity=0.4).add_to(mapa)
    return folium_static(mapa)
```

```python
# Carregando a função read_data()
dataframe_st = read_data()

# Funções utilizadas para a construção dos filtros (barra lateral)
st.sidebar.title('Localização e atributos')
# Acrescentação de checkboxs para demonstrar a tabela e o mapa
show_dataframe = st.sidebar.checkbox('Mostrar tabela', True)
show_map = st.sidebar.checkbox('Mostrar mapa')
# Filtragem por ID das casas (múltiplas casas podem ser selecionadas)
filter_id = st.sidebar.multiselect('ID das casas', dataframe_st['id'].unique().tolist())
# Filtro por preço
filter_price = st.sidebar.slider('Preço das casas', int(dataframe_st['price'].min()), int(dataframe_st['price'].max()),
                                 int(dataframe_st['price'].mean()))
# Filtro por número de banheiros, quartos e se a casa possui beira-mar
filter_bedrooms = st.sidebar.selectbox('Número de quartos', dataframe_st['bedrooms'].sort_values().unique().tolist())
filter_bathrooms = st.sidebar.selectbox('Número de banheiros',
                                        dataframe_st['bathrooms'].sort_values().unique().tolist())
filter_waterfront = st.sidebar.selectbox('Beira-mar', dataframe_st['waterfront'].unique().tolist())
```

```python
# Execução do filtro sobre os IDs das casas
if filter_id:
    dataframe_st = dataframe_st.loc[dataframe_st['id'].isin(filter_id)]
else:
    dataframe_st = dataframe_st.loc[(dataframe_st['price'] <= filter_price) &
                                    (dataframe_st['bedrooms'].isin([filter_bedrooms])) &
                                    (dataframe_st['bathrooms'].isin([filter_bathrooms])) &
                                    (dataframe_st['waterfront'].isin([filter_waterfront]))]
# Mostrando apenas a tabela
if show_dataframe:
    st.dataframe(dataframe_st)
    st.info(f'Total de {len(dataframe_st)} casas')
# Mostrando mapa e tabela (Se o total de casas for 0, demonstrará nada)
if (show_map == True) & (show_dataframe == True) & (len(dataframe_st) != 0):
    load_map(data=dataframe_st[['id', 'zipcode', 'lat', 'long', 'price', 'bedrooms', 'bathrooms', 'waterfront']])
# Mostrando apenas o mapa (Se o total de casas for 0, demonstrará nada)
if (show_map == True) & (show_dataframe == False) & (len(dataframe_st) != 0):
    st.info(f'Total de {len(dataframe_st)} casas')
    load_map(data=dataframe_st[['id', 'zipcode', 'lat', 'long', 'price', 'bedrooms', 'bathrooms', 'waterfront']])
```
# SUMMARY
House Rocket is a digital platform whose business model is the purchase and sale of properties using technology. The platform needs a better way to search for good homebuying opportunities in Seattle.

# INTRODUCTION
The application makes it possible to use a filter to facilitate the search for houses by price, number of bathrooms, bedrooms and whether it is by the sea so that these houses are shown on a map that divides the areas by average price and shows the information of each house next to a table.

# SOLUTION
Taking data from kaggle (https://www.kaggle.com/shivachandel/kc-house-data), and importing it into Jupyter Notebook to perform exploratory data analysis, it is possible to create insights for better solution development and discover data that tends to be unnecessary for the application. Applying data cleaning and transformation, which will improve what we need to solve the problem, from pycharm, and selecting the best attributes, taking into account what is requested, it is possible to build a report using the map and filters that are placed in production on Streamlit, thus facilitating decision making. The data collected for the construction of the map (https://data-seattlecitygis.opendata.arcgis.com/datasets/SeattleCityGIS::zip-codes/explore?location=47.243611%2C-121.083221%2C7.39).

# TOOLS
Python 3.9.13

PyCharm Community Edition 2022.1.3

folium 0.12.1

geopandas 0.10.2

numpy 1.20.3

pandas 1.2.4

plotly 5.4.0

streamlit 1.5.1

streamlit-folium 0.5.0

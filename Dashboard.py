import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if(valor < 1000):
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.3} milhões'
         

st.title("DASHBOARD DE VENDAS :shopping_trolley:")


# Importar os dados de uma API
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')

# Label e dados
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)

if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {
    'regiao': regiao.lower(),
    'ano': ano
}

response = requests.get(url, params=query_string)

# Transformar o JSON em um data frame
dados = pd.DataFrame.from_dict(response.json())

# Ajustar o formato da coluna de datas
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())

if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

#----------- Tabelas

## Tabelas Receitas

#Tabela com total de vendas, nome, latitude e logitude 
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index= True).sort_values('Preço', ascending=False)

#Tabela com a receita mensal 
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

#Receita por categoria
receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## Tabelas Vendas

#Quantidade de vendas por estado
vendas_estado = dados.groupby('Local da compra')[['Preço']].count()
vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on='Local da compra', right_index= True).sort_values('Preço', ascending=False)

#Quantidade de vendas mensais
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq= 'ME'))['Preço'].count().reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()


#Quantidade de vendas por categoria
vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

## Tabelas Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


#---------- Gráficos
#Receita total para cada estado (gráfico do pais)

fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', 
                                  hover_data = {'lat': False, 'lon': False}, #remove os dados de lat e lon
                                  title = 'Receita por estado') 

fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers=True, #Adiciona um marcador no mês
                             range_y= (0,receita_mensal.max()), #Para inciar o gráfico em 0
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')
# Altera a label do eixo y
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True, #Exibir o valor nas colunas
                             title= 'Top estados (Receita)')

# Altera a label do eixo y
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categoria.head(),
                             text_auto=True, #Exibir o valor nas colunas
                             title= 'Receita por categoria')

fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## Vendas

fig_mapa_vendas = px.scatter_geo(vendas_estado,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra', 
                                  hover_data = {'lat': False, 'lon': False}, #remove os dados de lat e lon
                                  title = 'Vendas por estado') 

fig_vendas_mensal = px.line(vendas_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers=True, #Adiciona um marcador no mês
                             range_y= (0,receita_mensal.max()), #Para inciar o gráfico em 0
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Vendas')


fig_vendas_estados = px.bar(vendas_estado.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True, #Exibir o valor nas colunas
                             title= 'Top estados (vendas)')
fig_vendas_estados.update_layout(yaxis_title = 'Vendas')


fig_vendas_categorias = px.bar(vendas_categorias.head(),
                             text_auto=True, #Exibir o valor nas colunas
                             title= 'Vendas por categoria')

fig_vendas_categorias.update_layout(yaxis_title = 'Vendas')



#----------- Viualização

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])



with aba1:
    #Colunas para o layout
    coluna1, coluna2 = st.columns(2)
    #Incluindo métricas
    with coluna1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0])) #quantidade de linhas do dataframe
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)
with aba2:
    #Colunas para o layout
    coluna1, coluna2 = st.columns(2)
    #Incluindo métricas
    with coluna1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0])) #quantidade de linhas do dataframe
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)
with aba3:
    quantidade_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    #Incluindo métricas
    with coluna1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
        vendedores_filtered = vendedores[['sum']].sort_values('sum', ascending=False).head(quantidade_vendedores)
        fig_receita_vendedores = px.bar(vendedores_filtered,
                                        x = 'sum', #Soma total da receita
                                        y = vendedores_filtered.index, #Nome dos vendendores
                                        text_auto=True,
                                        title= f'Top {quantidade_vendedores} vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores) 
    with coluna2:
        st.metric("Quantidade de vendas", formata_numero(dados.shape[0])) #quantidade de linhas do dataframe
        vendedores_filtered = vendedores[['count']].sort_values('count', ascending=False).head(quantidade_vendedores)
        fig_vendas_vendedores = px.bar(vendedores_filtered,
                                        x = 'count', #Soma total da receita
                                        y = vendedores_filtered.index, #Nome dos vendendores
                                        text_auto=True,
                                        title= f'Top {quantidade_vendedores} vendedores (Vendas)')
        st.plotly_chart(fig_vendas_vendedores) 

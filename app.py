import pandas as pd
import streamlit as st
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

# Caminho para a imagem
image_path = 'https://raw.githubusercontent.com/lcbueno/streamlit/main/yamaha.png'

# Exibir a imagem na barra lateral
st.sidebar.image(image_path, use_column_width=True)

# Estilo da barra lateral (mantendo a cor azul nos botões)
st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #262730;
            padding: 10px;
        }
        .sidebar .sidebar-content h2 {
            color: white;
            font-size: 24px;
            margin-bottom: 10px;
        }
        .stButton > button {
            font-size: 18px;
            color: white;
            background-color: #1F77B4;
            border: none;
            padding: 10px 20px;
            margin-bottom: 10px;
            width: 100%;
            text-align: left;
            border-radius: 5px;
        }
        .stButton > button:hover {
            background-color: #0073e6;
        }
        .stButton > button:focus {
            background-color: #005bb5;
        }
        .stContainer > div {
            display: flex;
            justify-content: space-around;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar para seleção da página principal
st.sidebar.title("Analytical Dashboard")
if st.sidebar.button("Overview Data"):
    st.session_state['page'] = 'Overview'
if st.sidebar.button("Regional Sales"):
    st.session_state['page'] = 'Regional Sales'
if st.sidebar.button("Vehicle Sales"):
    st.session_state['page'] = 'Vendas Carros'
if st.sidebar.button("Customer Profile"):
    st.session_state['page'] = 'Perfil do Cliente'

# Botão de upload do arquivo CSV abaixo dos botões de seleção de página
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Inicializar o estado da sessão para a página principal
if 'page' not in st.session_state:
    st.session_state['page'] = 'Overview Data'

if uploaded_file is not None:
    # Carregar o dataset com a codificação correta
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')

    # Converter a coluna "Date" para datetime sem exibir a mensagem de aviso
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    # Remover qualquer linha com datas inválidas (NaT)
    df = df.dropna(subset=['Date'])

    # Aplicar filtros (sem mostrar no layout)
    regions = df['Dealer_Region'].unique()
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    selected_region = regions  # Aplica automaticamente todas as regiões
    selected_dates = [min_date, max_date]  # Aplica automaticamente o intervalo completo

    # Converter selected_dates para datetime64
    selected_dates = pd.to_datetime(selected_dates)

    # Filtrando o DataFrame para todas as páginas
    filtered_df = df[(df['Dealer_Region'].isin(selected_region)) & 
                     (df['Date'].between(selected_dates[0], selected_dates[1]))]

    # Página: Visão Geral Dados
    if st.session_state['page'] == "Overview":
        st.title('Dashboard Yamaha - Overview Data')

        # Inicializar o estado da sessão para os gráficos se ainda não foi definido
        if 'chart_type' not in st.session_state:
            st.session_state['chart_type'] = 'Overview'

        # Botões no topo para escolher o gráfico
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Overview"):
                st.session_state['chart_type'] = "Overview"
        with col2:
            if st.button("Unique Values"):
                st.session_state['chart_type'] = "Unique Values"
        with col3:
            if st.button("Download Dataset"):
                st.session_state['chart_type'] = "Download Dataset"

        # Exibir o gráfico com base na escolha do botão
        if st.session_state['chart_type'] == 'Overview':
            st.write("DataFrame Visualization:")
            st.dataframe(df, width=1500, height=600)

        elif st.session_state['chart_type'] == 'Unique Values':
            unique_counts = df.nunique()
            st.write("Count unique values ​​per column:")
            st.write(unique_counts)

        elif st.session_state['chart_type'] == 'Download Dataset':
            st.download_button(
                label="Download Full Dataset",
                data=df.to_csv(index=False),
                file_name='dataset_completo.csv',
                mime='text/csv',
            )

    # Página: Vendas Regionais
    elif st.session_state['page'] == "Regional Sales":
        st.title('Dashboard Yamaha - Regional Sales')

        # Inicializar o estado da sessão para os gráficos se ainda não foi definido
        if 'chart_type' not in st.session_state:
            st.session_state['chart_type'] = 'Distribuição de Vendas por Região'

        # Botões no topo para escolher o gráfico
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("Sales by Region"):
                st.session_state['chart_type'] = "Distribuição de Vendas por Região"
        with col2:
            if st.button("Sales Evolution Over Time"):
                st.session_state['chart_type'] = "Evolução de Vendas"
        with col3:
            if st.button("Sales Evolution by Region"):
                st.session_state['chart_type'] = "Evolução de Vendas por Região"
        with col4:
            if st.button("Region x Vehicle Model"):
                st.session_state['chart_type'] = "Séries Temporais por Região e Modelo"
        with col5:
            if st.button("Product Mix Heatmap"):
                st.session_state['chart_type'] = "Heatmap do Mix de Produtos"

        # Exibir o gráfico com base na escolha do botão
        if st.session_state['chart_type'] == 'Distribuição de Vendas por Região':
            sales_by_region = filtered_df['Dealer_Region'].value_counts().reset_index()
            sales_by_region.columns = ['Dealer_Region', 'count']
            fig1 = px.pie(sales_by_region, names='Dealer_Region', values='count', title='Sales by Region')
            st.plotly_chart(fig1)

        elif st.session_state['chart_type'] == 'Evolução de Vendas':
            sales_over_time = filtered_df.groupby('Date').size().reset_index(name='Counts')
            fig4 = px.line(sales_over_time, x='Date', y='Counts', title='Sales Evolution Over Time')
            st.plotly_chart(fig4)

        elif st.session_state['chart_type'] == 'Evolução de Vendas por Região':
            sales_over_time_region = df.groupby([df['Date'].dt.to_period('M'), 'Dealer_Region']).size().unstack().fillna(0).reset_index()
            sales_over_time_region['Date'] = sales_over_time_region['Date'].astype(str)

            fig9 = px.line(sales_over_time_region, 
                           x='Date', 
                           y=sales_over_time_region.columns[1:], 
                           title='Evolution of Sales Over Time by Region',
                           labels={'value': 'Number of Sales', 'Date': 'Month'},
                           color_discrete_sequence=px.colors.qualitative.Set1)

            st.plotly_chart(fig9)

        elif st.session_state['chart_type'] == 'Séries Temporais por Região e Modelo':
            selected_region_time_series = st.selectbox('Select Region', regions)
            selected_model_time_series = st.selectbox('Select Vehicle Model', df['Model'].unique())

            def plot_sales(region, model):
                sales_time = df[(df['Dealer_Region'] == region) & (df['Model'] == model)].groupby(df['Date'].dt.to_period('M')).size()
                plt.figure(figsize=(14, 8))
                sales_time.plot(kind='line', marker='o', color='#FF7F0E', linewidth=2, markersize=6)
                plt.title(f'Monthly Sales - Region: {region}, Model: {model}', fontsize=16)
                plt.xlabel('Mês', fontsize=14)
                plt.ylabel('Number of Sales', fontsize=14)
                plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                plt.gca().spines['top'].set_color('none')
                plt.gca().spines['right'].set_color('none')
                plt.gca().set_facecolor('white')
                plt.gca().xaxis.label.set_color('black')
                plt.gca().yaxis.label.set_color('black')
                plt.gca().title.set_color('black')
                plt.gca().tick_params(axis='x', colors='black')
                plt.gca().tick_params(axis='y', colors='black')
                st.pyplot(plt)

            plot_sales(selected_region_time_series, selected_model_time_series)

        elif st.session_state['chart_type'] == 'Heatmap do Mix de Produtos':
            mix_product_region = df.groupby(['Dealer_Region', 'Body Style']).size().unstack().fillna(0)
            plt.figure(figsize=(12, 8))
            sns.heatmap(mix_product_region, annot=True, cmap='coolwarm', fmt='g')

            # Assegurando que as legendas e rótulos sejam visíveis
            plt.title('Product Mix by Region (Body Style)', fontsize=16)
            plt.xlabel('Body Style', fontsize=14)
            plt.ylabel('Reseller Region', fontsize=14)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            st.pyplot(plt)

    # Página: Vendas Carros
    elif st.session_state['page'] == "Vendas Carros":
        st.title('Dashboard Yamaha - Vehicle Sales')

        # Inicializar o estado da sessão para os gráficos se ainda não foi definido
        if 'chart_type' not in st.session_state:
            st.session_state['chart_type'] = 'Receita Média por Tipo de Carro'

        # Botões no topo para escolher o gráfico
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Average Revenue by Car Type"):
                st.session_state['chart_type'] = "Receita Média por Tipo de Carro"
        with col2:
            if st.button("Top 10 Companies by Revenue"):
                st.session_state['chart_type'] = "Top 10 Empresas por Receita"
        with col3:
            if st.button("Transmission Distribution by Engine"):
                st.session_state['chart_type'] = "Distribuição de Transmissão por Motor"

        # Exibir o gráfico com base na escolha do botão
        if st.session_state['chart_type'] == 'Receita Média por Tipo de Carro':
            avg_price_by_body = filtered_df.groupby('Body Style')['Price ($)'].mean().reset_index()
            fig2 = px.bar(avg_price_by_body, x='Body Style', y='Price ($)', title='Average Revenue by Car Type')
            st.plotly_chart(fig2)

        elif st.session_state['chart_type'] == 'Top 10 Empresas por Receita':
            top_companies = filtered_df.groupby('Company')['Price ($)'].sum().reset_index().sort_values(by='Price ($)', ascending=False).head(10)
            fig5 = px.bar(top_companies, x='Company', y='Price ($)', title='Top 10 Companies by Revenue')
            st.plotly_chart(fig5)

        elif st.session_state['chart_type'] == 'Distribuição de Transmissão por Motor':
            transmission_distribution = filtered_df.groupby(['Engine', 'Transmission']).size().reset_index(name='Counts')
            fig6 = px.bar(transmission_distribution, x='Engine', y='Counts', color='Transmission', barmode='group', title='Transmission Distribution by Engine')
            st.plotly_chart(fig6)

    # Página: Perfil do Cliente
    elif st.session_state['page'] == "Perfil do Cliente":
        st.title('Dashboard Yamaha - Customer Profile')

        # Inicializar o estado da sessão para os gráficos se ainda não foi definido
        if 'chart_type' not in st.session_state:
            st.session_state['chart_type'] = 'Distribuição de Gênero por Região'

        # Botões no topo para escolher o gráfico
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Gender Distribution by Region"):
                st.session_state['chart_type'] = "Distribuição de Gênero por Região"
        with col2:
            if st.button("Top 10 Models by Gender"):
                st.session_state['chart_type'] = "Top 10 Modelos por Gênero"

        # Exibir o gráfico com base na escolha do botão
        if st.session_state['chart_type'] == 'Distribuição de Gênero por Região':
            gender_distribution = filtered_df.groupby(['Dealer_Region', 'Gender']).size().reset_index(name='Counts')
            fig3 = px.bar(gender_distribution, x='Dealer_Region', y='Counts', color='Gender', barmode='group', title='Gender Distribution by Region')
            st.plotly_chart(fig3)

        elif st.session_state['chart_type'] == 'Top 10 Modelos por Gênero':
            top_10_male_models = filtered_df[filtered_df['Gender'] == 'Male']['Model'].value_counts().head(10)
            top_10_female_models = filtered_df[filtered_df['Gender'] == 'Female']['Model'].value_counts().head(10)

            top_10_models_df = pd.DataFrame({
                'Male': top_10_male_models,
                'Female': top_10_female_models
            }).fillna(0)

            top_10_models_df_sorted = top_10_models_df.sort_values(by=['Male', 'Female'], ascending=False)

            fig7 = px.bar(top_10_models_df_sorted, 
                          x=top_10_models_df_sorted.index, 
                          y=['Male', 'Female'], 
                          title='Top 10 Models by Gender',
                          labels={'value': 'Number of Sales', 'index': 'Models'},
                          barmode='group')

            st.plotly_chart(fig7)
else:
    st.warning("Por favor, carregue um arquivo CSV para visualizar os dados.")

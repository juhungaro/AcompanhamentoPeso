import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

# Configurações da página
st.set_page_config(page_title="Monitoramento Físico", layout="wide")

# Funções auxiliares
def load_data():
    try:
        df = pd.read_csv("dados_alunos.csv")
        # Converter colunas numéricas
        numeric_columns = ["Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q", "Percentual_Gordura", "Percentual_Massa_Magra", "Gordura_Visceral"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Converter a coluna de data, lidando com diferentes formatos
        df["Data"] = pd.to_datetime(df["Data"], format='mixed', dayfirst=True, errors='coerce')
        
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q", "Percentual_Gordura", "Percentual_Massa_Magra", "Gordura_Visceral", "Meta_Peso", "Meta_Cintura", "Meta_Gordura"])

def calculate_imc(peso, altura):
    try:
        return round(float(peso) / (float(altura) ** 2), 2)
    except:
        return None

def calculate_rcq(cintura, quadril):
    try:
        return round(float(cintura) / float(quadril), 2)
    except:
        return None

def get_imc_classification(imc):
    try:
        imc = float(imc)
        if imc < 18.5:
            return "Magreza", "warning"
        elif imc < 24.9:
            return "Peso normal", "success"
        elif imc < 29.9:
            return "Sobrepeso", "warning"
        elif imc < 34.9:
            return "Obesidade Grau I", "error"
        elif imc < 39.9:
            return "Obesidade Grau II", "error"
        else:
            return "Obesidade Grau III", "error"
    except:
        return "IMC inválido", "error"

def criar_dashboard(dados):
    st.header("Dashboard - Visão Geral dos Alunos")
    total_alunos = dados['Nome'].nunique()
    st.metric("Total de Alunos", total_alunos, key="metric_total_alunos")

    fig_imc, ax_imc = plt.subplots(figsize=(10, 6))
    dados.groupby('Nome')['IMC'].last().hist(bins=20, ax=ax_imc)
    ax_imc.set_title("Distribuição do IMC dos Alunos")
    ax_imc.set_xlabel("IMC")
    ax_imc.set_ylabel("Número de Alunos")
    st.pyplot(fig_imc, key="plot_distribuicao_imc")

    dados_recentes = dados.sort_values('Data').groupby('Nome').last().reset_index()
    st.subheader("Resumo dos Dados Mais Recentes", key="subheader_resumo_dados")
    st.dataframe(dados_recentes[['Nome', 'Data', 'Peso', 'Altura', 'IMC', 'Cintura', 'Quadril']], key="dataframe_resumo")

    fig_peso, ax_peso = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Peso'].mean().plot(ax=ax_peso)
    ax_peso.set_title("Evolução Média do Peso dos Alunos")
    ax_peso.set_xlabel("Data")
    ax_peso.set_ylabel("Peso Médio (kg)")
    st.pyplot(fig_peso, key="plot_evolucao_peso")

# Interface principal
st.title("Monitoramento de Peso e Medidas")
st.markdown("### Acompanhe o progresso físico com base em dados de peso, medidas e parâmetros da OMS")

# Menu lateral
menu = st.sidebar.selectbox("Escolha uma opção", ["Inserir Dados", "Visualizar Aluno", "Dashboard"], key="menu_principal")

if menu == "Inserir Dados":
    st.sidebar.header("Inserir dados do aluno")
    with st.sidebar.form("entrada_dados"):
        nome = st.text_input("Nome do aluno", key="input_nome")
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], key="select_sexo")
        altura = st.number_input("Altura (em metros)", format="%.2f", min_value=0.1, max_value=3.0, step=0.01, key="input_altura")
        peso = st.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1, key="input_peso")
        cintura = st.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1, key="input_cintura")
        quadril = st.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1, key="input_quadril")
        perc_gordura = st.number_input("Percentual de Gordura (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1, key="input_gordura")
        perc_massa_magra = st.number_input("Percentual de Massa Magra (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1, key="input_massa_magra")
        gordura_visceral = st.number_input("Gordura Visceral", format="%.1f", min_value=0.0, step=0.1, key="input_gordura_visceral")
        
        st.subheader("Metas")
        meta_peso = st.number_input("Meta de Peso (kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1, key="input_meta_peso")
        meta_cintura = st.number_input("Meta de Circunferência da Cintura (cm)", format="%.1f", min_value=0.0, step=0.1, key="input_meta_cintura")
        meta_gordura = st.number_input("Meta de Percentual de Gordura (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1, key="input_meta_gordura")
        
        data = st.date_input("Data da medição", value=dt.date.today(), key="input_data")
        submitted = st.form_submit_button("Salvar Dados")

    if submitted:
        if nome and altura > 0 and peso > 0:
            dados = load_data()
            imc = calculate_imc(peso, altura)
            rcq = calculate_rcq(cintura, quadril)
            novo_dado = pd.DataFrame({
                "Nome": [nome], "Sexo": [sexo], "Data": [data.strftime('%Y-%m-%d')],
                "Altura": [altura], "Peso": [peso], "Cintura": [cintura], "Quadril": [quadril],
                "IMC": [imc], "C/Q": [rcq], "Percentual_Gordura": [perc_gordura],
                "Percentual_Massa_Magra": [perc_massa_magra], "Gordura_Visceral": [gordura_visceral],
                "Meta_Peso": [meta_peso], "Meta_Cintura": [meta_cintura], "Meta_Gordura": [meta_gordura]
            })
            dados = pd.concat([dados, novo_dado], ignore_index=True)
            dados.to_csv("dados_alunos.csv", index=False)
            st.sidebar.success(f"Dados salvos com sucesso! IMC calculado: {imc}")
        else:
            st.sidebar.error("Preencha todos os campos obrigatórios!")

elif menu == "Visualizar Aluno":
    dados = load_data()
    if not dados.empty:
        alunos = dados["Nome"].unique()
        aluno_selecionado = st.selectbox("Selecione um aluno", alunos, key="select_aluno_visualizar")
        
        if aluno_selecionado:
            dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            # ... (código para métricas permanece o mesmo)

            # Análise do IMC
            st.subheader("Análise do IMC")
            # ... (código para análise do IMC permanece o mesmo)

            # Usando st.radio() para criar as "tabs"
            tab_selecionada = st.radio(
                "Selecione o gráfico:",
                ["Progresso do Peso", "Medidas Corporais", "Gordura Visceral", "Massa Muscular", "Gordura Corporal"]
            )
            
            if tab_selecionada == "Progresso do Peso":
                # Gráfico de Progresso do Peso
                # ... (código existente para o gráfico de peso)

            elif tab_selecionada == "Medidas Corporais":
                # Gráficos de Cintura e Quadril
                # ... (código existente para os gráficos de cintura e quadril)

            elif tab_selecionada == "Gordura Visceral":
                # Gráfico para Gordura Visceral
                dados_gordura_visceral = dados_aluno.dropna(subset=['Gordura_Visceral'])
                if not dados_gordura_visceral.empty:
                    fig_gv, ax_gv = plt.subplots(figsize=(10, 6))
                    ax_gv.plot(dados_gordura_visceral["Data"], dados_gordura_visceral["Gordura_Visceral"], marker="o", linewidth=2, color='#2E86C1')
                    
                    ax_gv.axhspan(0, 9, facecolor='green', alpha=0.3, label='Normal')
                    ax_gv.axhspan(9, 14, facecolor='yellow', alpha=0.3, label='Alto')
                    ax_gv.axhspan(14, 30, facecolor='red', alpha=0.3, label='Muito Alto')
                    
                    ax_gv.set_title("Progresso da Gordura Visceral", pad=20, fontsize=14)
                    ax_gv.set_xlabel("Data", fontsize=12)
                    ax_gv.set_ylabel("Nível de Gordura Visceral", fontsize=12)
                    ax_gv.grid(True, alpha=0.3)
                    ax_gv.legend()
                    
                    plt.xticks(dados_gordura_visceral["Data"], dados_gordura_visceral["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig_gv)
                    plt.close()
                    
                    st.markdown("""
                    <small>
                    * Referências de Gordura Visceral:<br>
                    - Verde: Normal (1-9)<br>
                    - Amarelo: Alto (10-14)<br>
                    - Vermelho: Muito Alto (15+)
                    </small>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Não há dados de Gordura Visceral para exibir no gráfico")

            elif tab_selecionada == "Massa Muscular":
                # Gráfico para Massa Muscular
                dados_massa_muscular = dados_aluno.dropna(subset=['Percentual_Massa_Magra'])
                if not dados_massa_muscular.empty:
                    fig_mm, ax_mm = plt.subplots(figsize=(10, 6))
                    ax_mm.plot(dados_massa_muscular["Data"], dados_massa_muscular["Percentual_Massa_Magra"], marker="o", linewidth=2, color='#27AE60')
                    
                    ax_mm.set_title("Progresso da Massa Muscular", pad=20, fontsize=14)
                    ax_mm.set_xlabel("Data", fontsize=12)
                    ax_mm.set_ylabel("Percentual de Massa Muscular", fontsize=12)
                    ax_mm.grid(True, alpha=0.3)
                    
                    plt.xticks(dados_massa_muscular["Data"], dados_massa_muscular["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig_mm)
                    plt.close()
                else:
                    st.warning("Não há dados de Massa Muscular para exibir no gráfico")

            elif tab_selecionada == "Gordura Corporal":
                # Gráfico para Gordura Corporal
                dados_gordura_corporal = dados_aluno.dropna(subset=['Percentual_Gordura'])
                if not dados_gordura_corporal.empty:
                    fig_gc, ax_gc = plt.subplots(figsize=(10, 6))
                    ax_gc.plot(dados_gordura_corporal["Data"], dados_gordura_corporal["Percentual_Gordura"], marker="o", linewidth=2, color='#E74C3C')
                    
                    ax_gc.set_title("Progresso da Gordura Corporal", pad=20, fontsize=14)
                    ax_gc.set_xlabel("Data", fontsize=12)
                    ax_gc.set_ylabel("Percentual de Gordura Corporal", fontsize=12)
                    ax_gc.grid(True, alpha=0.3)
                    
                    plt.xticks(dados_gordura_corporal["Data"], dados_gordura_corporal["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig_gc)
                    plt.close()
                else:
                    st.warning("Não há dados de Gordura Corporal para exibir no gráfico")

    else:
        st.warning("Não há dados disponíveis para visualização.")

elif menu == "Dashboard":
    dados = load_data()
    criar_dashboard(dados)



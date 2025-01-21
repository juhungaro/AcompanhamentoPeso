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
        numeric_columns = ["Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

def calculate_imc(peso, altura):
    try:
        peso = float(peso)
        altura = float(altura)
        if altura > 0 and peso > 0:
            return round(peso / (altura ** 2), 2)
        return None
    except (ValueError, TypeError):
        return None

def calculate_rcq(cintura, quadril):
    try:
        cintura = float(cintura)
        quadril = float(quadril)
        if quadril > 0 and cintura > 0:
            return round(cintura / quadril, 2)
        return None
    except (ValueError, TypeError):
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
    except (ValueError, TypeError):
        return "IMC inválido", "error"

# Interface principal
st.title("Monitoramento de Peso e Medidas")
st.markdown("### Acompanhe o progresso físico com base em dados de peso, medidas e parâmetros da OMS")

# Sidebar para entrada de dados
with st.sidebar:
    st.title("Menu")
    st.header("Inserir dados do aluno")
    
    # Formulário de entrada
    with st.form("entrada_dados"):
        nome = st.text_input("Nome do aluno")
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        altura = st.number_input("Altura (em metros)", format="%.2f", min_value=0.1, max_value=3.0, step=0.01)
        peso = st.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1)
        cintura = st.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1)
        quadril = st.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1)
        data = st.date_input("Data da medição", value=dt.date.today())
        
        submitted = st.form_submit_button("Salvar Dados")

# Processamento do formulário
if submitted:
    if nome and altura > 0 and peso > 0:
        dados = load_data()
        
        # Calcular IMC e RCQ
        imc = calculate_imc(peso, altura)
        rcq = calculate_rcq(cintura, quadril)
        
        novo_dado = pd.DataFrame({
            "Nome": [nome],
            "Sexo": [sexo],
            "Data": [data],
            "Altura": [altura],
            "Peso": [peso],
            "Cintura": [cintura],
            "Quadril": [quadril],
            "IMC": [imc],
            "C/Q": [rcq]
        })
        
        dados = pd.concat([dados, novo_dado], ignore_index=True)
        dados.to_csv("dados_alunos.csv", index=False)
        st.sidebar.success(f"Dados salvos com sucesso! IMC calculado: {imc}")
    else:
        st.sidebar.error("Preencha todos os campos obrigatórios!")

# Visualização dos dados
try:
    dados = load_data()
    
    if not dados.empty:
        dados["Data"] = pd.to_datetime(dados["Data"])
        
        # Seleção do aluno
        alunos = dados["Nome"].unique()
        col1, col2 = st.columns([2, 1])
        with col1:
            aluno_selecionado = st.selectbox("Selecione um aluno", alunos)
        
        if aluno_selecionado:
            dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Peso Atual", f"{dados_aluno['Peso'].iloc[-1]:.1f} kg")
            with col2:
                imc_atual = dados_aluno['IMC'].iloc[-1]
                st.metric("IMC Atual", f"{imc_atual:.1f}")
            with col3:
                st.metric("Cintura", f"{dados_aluno['Cintura'].iloc[-1]:.1f} cm")
            with col4:
                st.metric("Quadril", f"{dados_aluno['Quadril'].iloc[-1]:.1f} cm")
            
            # Classificação IMC
            st.subheader("Análise do IMC")
            classificacao, nivel = get_imc_classification(imc_atual)
            
            if nivel == "success":
                st.success(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            elif nivel == "warning":
                st.warning(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            else:
                st.error(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")

                   
            # Tabela de dados
            st.subheader("Histórico de Medições")
            st.dataframe(dados_aluno.sort_values("Data", ascending=False))
            
            # Botão de download
            csv = dados_aluno.to_csv(index=False)
            st.download_button(
                label="Download dos dados",
                data=csv,
                file_name=f"dados_{aluno_selecionado}.csv",
                mime="text/csv"
            )
            
    else:
        st.info("Nenhum dado encontrado. Insira os dados de um aluno para começar!")
        
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")

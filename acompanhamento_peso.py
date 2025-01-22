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
        numeric_columns = ["Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q", 
                           "Percentual_Gordura", "Percentual_Massa_Magra", "Gordura_Visceral",
                           "Meta_Peso", "Meta_Cintura", "Meta_Gordura"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Converter a coluna de data, lidando com diferentes formatos
        df["Data"] = pd.to_datetime(df["Data"], format='mixed', dayfirst=True, errors='coerce')
        
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", 
                                     "IMC", "C/Q", "Percentual_Gordura", "Percentual_Massa_Magra", 
                                     "Gordura_Visceral", "Meta_Peso", "Meta_Cintura", "Meta_Gordura"])

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
    st.metric("Total de Alunos", total_alunos)

    fig_imc, ax_imc = plt.subplots(figsize=(10, 6))
    dados.groupby('Nome')['IMC'].last().hist(bins=20, ax=ax_imc)
    ax_imc.set_title("Distribuição do IMC dos Alunos")
    ax_imc.set_xlabel("IMC")
    ax_imc.set_ylabel("Número de Alunos")
    st.pyplot(fig_imc)

    dados_recentes = dados.sort_values('Data').groupby('Nome').last().reset_index()
    st.subheader("Resumo dos Dados Mais Recentes")
    st.dataframe(dados_recentes[['Nome', 'Data', 'Peso', 'Altura', 'IMC', 'Cintura', 'Quadril', 
                                 'Percentual_Gordura', 'Percentual_Massa_Magra', 'Gordura_Visceral']])

    fig_peso, ax_peso = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Peso'].mean().plot(ax=ax_peso)
    ax_peso.set_title("Evolução Média do Peso dos Alunos")
    ax_peso.set_xlabel("Data")
    ax_peso.set_ylabel("Peso Médio (kg)")
    st.pyplot(fig_peso)

    # Novos gráficos para as novas medidas
    fig_gordura, ax_gordura = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Percentual_Gordura'].mean().plot(ax=ax_gordura)
    ax_gordura.set_title("Evolução Média do Percentual de Gordura dos Alunos")
    ax_gordura.set_xlabel("Data")
    ax_gordura.set_ylabel("Percentual de Gordura Médio (%)")
    st.pyplot(fig_gordura)

    fig_visceral, ax_visceral = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Gordura_Visceral'].mean().plot(ax=ax_visceral)
    ax_visceral.set_title("Evolução Média da Gordura Visceral dos Alunos")
    ax_visceral.set_xlabel("Data")
    ax_visceral.set_ylabel("Gordura Visceral Média")
    st.pyplot(fig_visceral)

# Interface principal
st.title("Monitoramento de Peso e Medidas")
st.markdown("### Acompanhe o progresso físico com base em dados de peso, medidas e parâmetros da OMS")

# Menu lateral
menu = st.sidebar.selectbox("Escolha uma opção", ["Inserir Dados", "Visualizar Aluno", "Dashboard"])

if menu == "Inserir Dados":
    st.sidebar.header("Inserir dados do aluno")
    with st.sidebar.form("entrada_dados"):
        nome = st.text_input("Nome do aluno")
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        altura = st.number_input("Altura (em metros)", format="%.2f", min_value=0.1, max_value=3.0, step=0.01)
        peso = st.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1)
        cintura = st.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1)
        quadril = st.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1)
        perc_gordura = st.number_input("Percentual de Gordura (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1)
        perc_massa_magra = st.number_input("Percentual de Massa Magra (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1)
        gordura_visceral = st.number_input("Gordura Visceral", format="%.1f", min_value=0.0, step=0.1)
        
        st.subheader("Metas")
        meta_peso = st.number_input("Meta de Peso (kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1)
        meta_cintura = st.number_input("Meta de Circunferência da Cintura (cm)", format="%.1f", min_value=0.0, step=0.1)
        meta_gordura = st.number_input("Meta de Percentual de Gordura (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1)
        
        data = st.date_input("Data da medição", value=dt.date.today())
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
        aluno_selecionado = st.selectbox("Selecione um aluno", alunos)
        
        if aluno_selecionado:
            dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                peso_atual = dados_aluno['Peso'].iloc[-1] if not dados_aluno.empty else None
                meta_peso = dados_aluno['Meta_Peso'].iloc[-1] if not dados_aluno.empty else None
                st.metric("Peso Atual", f"{peso_atual:.1f} kg" if peso_atual is not None else "N/A")
                st.metric("Meta de Peso", f"{meta_peso:.1f} kg" if meta_peso is not None else "N/A")
            with col2:
                imc_atual = dados_aluno['IMC'].iloc[-1] if not dados_aluno.empty else None
                st.metric("IMC Atual", f"{imc_atual:.1f}" if imc_atual is not None else "N/A")
            with col3:
                cintura_atual = dados_aluno['Cintura'].iloc[-1] if not dados_aluno.empty else None
                meta_cintura = dados_aluno['Meta_Cintura'].iloc[-1] if not dados_aluno.empty else None
                st.metric("Cintura", f"{cintura_atual:.1f} cm" if cintura_atual is not None else "N/A")
                st.metric("Meta de Cintura", f"{meta_cintura:.1f} cm" if meta_cintura is not None else "N/A")
            with col4:
                gordura_atual = dados_aluno['Percentual_Gordura'].iloc[-1] if not dados_aluno.empty else None
                meta_gordura = dados_aluno['Meta_Gordura'].iloc[-1] if not dados_aluno.empty else None
                st.metric("% Gordura", f"{gordura_atual:.1f}%" if gordura_atual is not None else "N/A")
                st.metric("Meta % Gordura", f"{meta_gordura:.1f}%" if meta_gordura is not None else "N/A")
            
            st.subheader("Análise do IMC")
            if imc_atual is not None:
                classificacao, nivel = get_imc_classification(imc_atual)
                if nivel == "success":
                    st.success(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
                elif nivel == "warning":
                    st.warning(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
                else:
                    st.error(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            else:
                st.info("Dados de IMC não disponíveis")
            
            tab1, tab2 = st.tabs(["Progresso do Peso", "Medidas Corporais"])
            
            with tab1:
                dados_peso = dados_aluno.dropna(subset=['Peso'])
                if not dados_peso.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    altura_atual = dados_aluno['Altura'].iloc[-1]
                    imc_ranges = [
                        (0, 18.5, '#fff3cd', 'Magreza'),
                        (18.5, 24.9, '#d4edda', 'Normal'),
                        (25, 29.9, '#fff3cd', 'Sobrepeso'),
                        (30, 34.9, '#f8d7da', 'Obesidade I'),
                        (35, 39.9, '#f8d7da', 'Obesidade II'),
                        (40, 50, '#f8d7da', 'Obesidade III')
                    ]
                    y_min = dados_peso['Peso'].min() * 0.8
                    y_max = dados_peso['Peso'].max() * 1.2
                    for imc_min, imc_max, color, label in imc_ranges:
                        peso_min = (imc_min * (altura_atual ** 2))
                        peso_max = (imc_max * (altura_atual ** 2))
                        ax.axhspan(peso_min, peso_max, color=color, alpha=0.3, label=f'Faixa {label}')
                    ax.plot(dados_peso["Data"], dados_peso["Peso"], marker="o", linewidth=2, color='#2E86C1', label='Peso atual', zorder=5)
                    for x, y in zip(dados_peso["Data"], dados_peso["Peso"]):
                        ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, zorder=6)
                    ax.set_title("Progresso do Peso com Faixas de Referência IMC", pad=20, fontsize=14)
                    ax.set_xlabel("Data", fontsize=12)
                    ax.set_ylabel("Peso (kg)", fontsize=12)
                    ax.grid(True, alpha=0.3, zorder=1)
                    ax.set_ylim(y_min, y_max)
                    plt.xticks(dados_peso["Data"], dados_peso["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                    st.markdown("""
                    <small>
                    * As faixas coloridas representam as classificações de IMC da OMS:<br>
                    - Amarelo claro: Magreza (IMC < 18,5) e Sobrepeso (IMC 25-29,9)<br>
                    - Verde claro: Peso Normal (IMC 18,5-24,9)<br>
                    - Vermelho claro: Obesidade (IMC ≥ 30)
                    </small>

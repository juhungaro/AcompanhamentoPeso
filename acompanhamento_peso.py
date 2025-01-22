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
        
        # Converter a coluna de data, lidando com diferentes formatos
        df["Data"] = pd.to_datetime(df["Data"], format='mixed', dayfirst=True, errors='coerce')
        
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])


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
    st.dataframe(dados_recentes[['Nome', 'Data', 'Peso', 'Altura', 'IMC', 'Cintura', 'Quadril']])

    fig_peso, ax_peso = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Peso'].mean().plot(ax=ax_peso)
    ax_peso.set_title("Evolução Média do Peso dos Alunos")
    ax_peso.set_xlabel("Data")
    ax_peso.set_ylabel("Peso Médio (kg)")
    st.pyplot(fig_peso)

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
        data = st.date_input("Data da medição", value=dt.date.today())
        submitted = st.form_submit_button("Salvar Dados")

    if submitted:
        if nome and altura > 0 and peso > 0:
            dados = load_data()
            imc = calculate_imc(peso, altura)
            rcq = calculate_rcq(cintura, quadril)
            novo_dado = pd.DataFrame({
                "Nome": [nome], 
                "Sexo": [sexo], 
                "Data": [data.strftime('%Y-%m-%d')],  # Formato ISO para consistência 
                "Altura": [altura],
                "Peso": [peso], 
                "Cintura": [cintura], 
                "Quadril": [quadril],
                "IMC": [imc], "C/Q": [rcq]
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
        col1, col2 = st.columns([2, 1])
        with col1:
            aluno_selecionado = st.selectbox("Selecione um aluno", alunos)
        
               
        if aluno_selecionado:
            if st.button("Apagar Registro do Aluno"):
                confirma = st.checkbox("Confirmar exclusão")
                if confirma:
                    dados = dados[dados["Nome"] != aluno_selecionado]
                    dados.to_csv("dados_alunos.csv", index=False)
                    st.success(f"Registro de {aluno_selecionado} apagado com sucesso!")
                    st.experimental_rerun()
            
            dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")
            
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
            
            st.subheader("Análise do IMC")
            classificacao, nivel = get_imc_classification(imc_atual)
            if nivel == "success":
                st.success(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            elif nivel == "warning":
                st.warning(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            else:
                st.error(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            
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
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Não há dados de peso para exibir no gráfico")
            
            with tab2:
                dados_medidas = dados_aluno.dropna(subset=['Cintura', 'Quadril'])
                if not dados_medidas.empty:
                    sexo_atual = dados_aluno['Sexo'].iloc[0]
                    
                    # Gráfico da Cintura
                    fig_cintura, ax_cintura = plt.subplots(figsize=(10, 6))
                    if sexo_atual == "Masculino":
                        cintura_ranges = [
                            (0, 94, '#d4edda', 'Normal'),
                            (94, 102, '#fff3cd', 'Risco Aumentado'),
                            (102, 200, '#f8d7da', 'Risco Alto')
                        ]
                    else:
                        cintura_ranges = [
                            (0, 80, '#d4edda', 'Normal'),
                            (80, 88, '#fff3cd', 'Risco Aumentado'),
                            (88, 200, '#f8d7da', 'Risco Alto')
                        ]
                    
                    y_min_cintura = dados_medidas['Cintura'].min() * 0.9
                    y_max_cintura = dados_medidas['Cintura'].max() * 1.1
                    
                    for c_min, c_max, color, label in cintura_ranges:
                        ax_cintura.axhspan(c_min, c_max, color=color, alpha=0.3, label=f'Cintura: {label}')
                    
                    ax_cintura.plot(dados_medidas["Data"], dados_medidas["Cintura"], marker="o", label="Cintura", color='#E74C3C', linewidth=2, zorder=5)
                    
                    for x, y in zip(dados_medidas["Data"], dados_medidas["Cintura"]):
                        ax_cintura.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, zorder=6)
                    
                    ax_cintura.set_title(f"Medida da Cintura com Referências OMS ({sexo_atual})", pad=20, fontsize=14)
                    ax_cintura.set_xlabel("Data", fontsize=12)
                    ax_cintura.set_ylabel("Centímetros", fontsize=12)
                    ax_cintura.grid(True, alpha=0.3, zorder=1)
                    ax_cintura.set_ylim(y_min_cintura, y_max_cintura)
                    plt.xticks(dados_medidas["Data"], dados_medidas["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    ax_cintura.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.tight_layout()
                    st.pyplot(fig_cintura)
                    plt.close()
                    
                    # Gráfico do Quadril
                    fig_quadril, ax_quadril = plt.subplots(figsize=(10, 6))
                    y_min_quadril = dados_medidas['Quadril'].min() * 0.9
                    y_max_quadril = dados_medidas['Quadril'].max() * 1.1
                    
                    ax_quadril.plot(dados_medidas["Data"], dados_medidas["Quadril"], marker="o", label="Quadril", color='#8E44AD', linewidth=2, zorder=5)
                    
                    for x, y in zip(dados_medidas["Data"], dados_medidas["Quadril"]):
                        ax_quadril.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, zorder=6)
                    
                    ax_quadril.set_title(f"Medida do Quadril ({sexo_atual})", pad=20, fontsize=14)
                    ax_quadril.set_xlabel("Data", fontsize=12)
                    ax_quadril.set_ylabel("Centímetros", fontsize=12)
                    ax_quadril.grid(True, alpha=0.3, zorder=1)
                    ax_quadril.set_ylim(y_min_quadril, y_max_quadril)
                    plt.xticks(dados_medidas["Data"], dados_medidas["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    ax_quadril.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.tight_layout()
                    st.pyplot(fig_quadril)
                    plt.close()

                    if sexo_atual == "Masculino":
                        st.markdown("""
                        <small>
                        * Referências de Circunferência da Cintura (OMS) para homens:<br>
                        - Verde claro: Normal (< 94 cm)<br>
                        - Amarelo claro: Risco Aumentado (94-102 cm)<br>
                        - Vermelho claro: Risco Alto (> 102 cm)
                        </small>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <small>
                        * Referências de Circunferência da Cintura (OMS) para mulheres:<br>
                        - Verde claro: Normal (< 80 cm)<br>
                        - Amarelo claro: Risco Aumentado (80-88 cm)<br>
                        - Vermelho claro: Risco Alto (> 88 cm)
                        </small>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Não há dados de medidas suficientes para gerar os gráficos")

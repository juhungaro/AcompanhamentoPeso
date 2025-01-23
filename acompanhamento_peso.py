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
        numeric_columns = ["Altura", "Peso", "IMC", "Percentual_Gordura", "Percentual_Massa_Magra", "Gordura_Visceral"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df["Data"] = pd.to_datetime(df["Data"], format='mixed', dayfirst=True, errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "IMC", "Percentual_Gordura", "Percentual_Massa_Magra", "Gordura_Visceral"])

def calculate_imc(peso, altura):
    try:
        return round(float(peso) / (float(altura) ** 2), 2)
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

def get_gordura_visceral_classification(gv):
    if gv < 10:
        return "Normal", "success"
    elif gv < 15:
        return "Alto", "warning"
    else:
        return "Muito Alto", "error"

def get_gordura_corporal_classification(gc, sexo):
    if sexo == "Masculino":
        if gc < 6:
            return "Muito baixo", "warning"
        elif gc < 14:
            return "Atlético", "success"
        elif gc < 18:
            return "Bom", "success"
        elif gc < 25:
            return "Normal", "success"
        else:
            return "Alto", "error"
    else:  # Feminino
        if gc < 14:
            return "Muito baixo", "warning"
        elif gc < 21:
            return "Atlético", "success"
        elif gc < 25:
            return "Bom", "success"
        elif gc < 32:
            return "Normal", "success"
        else:
            return "Alto", "error"

def plot_metric_with_ranges(data, column, title, ylabel, ranges, ax):
    ax.plot(data["Data"], data[column], marker="o", linewidth=2, color='#2E86C1', zorder=5)
    
    y_min = data[column].min() * 0.9
    y_max = data[column].max() * 1.1
    
    for min_val, max_val, color, label in ranges:
        ax.axhspan(min_val, max_val, facecolor=color, alpha=0.3, label=label)
    
    ax.set_title(title, pad=20, fontsize=14)
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3, zorder=1)
    ax.set_ylim(y_min, y_max)
    
    for x, y in zip(data["Data"], data[column]):
        ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, zorder=6)
    
    plt.xticks(data["Data"], data["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

# Interface principal
st.title("Monitoramento de Peso e Medidas")
st.markdown("### Acompanhe o progresso físico com base em dados de peso e parâmetros da OMS")

# Menu lateral
menu = st.sidebar.selectbox("Escolha uma opção", ["Inserir Dados", "Visualizar Aluno"])

if menu == "Inserir Dados":
    st.sidebar.header("Inserir dados do aluno")
    with st.sidebar.form("entrada_dados"):
        nome = st.text_input("Nome do aluno")
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        altura = st.number_input("Altura (em metros)", format="%.2f", min_value=0.1, max_value=3.0, step=0.01)
        peso = st.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, max_value=300.0, step=0.1)
        perc_gordura = st.number_input("Percentual de Gordura (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1)
        perc_massa_magra = st.number_input("Percentual de Massa Magra (%)", format="%.1f", min_value=0.0, max_value=100.0, step=0.1)
        gordura_visceral = st.number_input("Gordura Visceral", format="%.1f", min_value=0.0, step=0.1)
        
        data = st.date_input("Data da medição", value=dt.date.today())
        submitted = st.form_submit_button("Salvar Dados")

    if submitted:
        if nome and altura > 0 and peso > 0:
            dados = load_data()
            imc = calculate_imc(peso, altura)
            novo_dado = pd.DataFrame({
                "Nome": [nome], "Sexo": [sexo], "Data": [data.strftime('%Y-%m-%d')],
                "Altura": [altura], "Peso": [peso], "IMC": [imc],
                "Percentual_Gordura": [perc_gordura], "Percentual_Massa_Magra": [perc_massa_magra],
                "Gordura_Visceral": [gordura_visceral]
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
            
            #col1, col2 = st.columns(2)
            #with col1:
                #peso_atual = dados_aluno['Peso'].iloc[-1] if not dados_aluno.empty else None
                #st.metric("Peso Atual", f"{peso_atual:.1f} kg" if peso_atual is not None else "N/A")
            #with col2:
                #imc_atual = dados_aluno['IMC'].iloc[-1] if not dados_aluno.empty else None
                #st.metric("IMC Atual", f"{imc_atual:.1f}" if imc_atual is not None else "N/A")
            
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
            
            tab_selecionada = st.radio(
                "Selecione o gráfico:",
                ["Progresso do Peso", "Gordura Visceral", "Gordura Corporal", "Massa Muscular"]
            )
            
            if tab_selecionada == "Progresso do Peso":
                dados_peso = dados_aluno.dropna(subset=['Peso'])
                if not dados_peso.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    altura_atual = dados_aluno['Altura'].iloc[-1]
                    imc_ranges = [
                        (0, 18.5 * (altura_atual ** 2), '#fff3cd', 'Magreza'),
                        (18.5 * (altura_atual ** 2), 24.9 * (altura_atual ** 2), '#d4edda', 'Normal'),
                        (25 * (altura_atual ** 2), 29.9 * (altura_atual ** 2), '#fff3cd', 'Sobrepeso'),
                        (30 * (altura_atual ** 2), 50 * (altura_atual ** 2), '#f8d7da', 'Obesidade')
                    ]
                    plot_metric_with_ranges(dados_peso, "Peso", "Progresso do Peso com Faixas de Referência IMC", "Peso (kg)", imc_ranges, ax)
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
            
            elif tab_selecionada == "Gordura Visceral":
                dados_gordura_visceral = dados_aluno.dropna(subset=['Gordura_Visceral'])
                if not dados_gordura_visceral.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    gv_ranges = [
                        (0, 9, '#d4edda', 'Normal'),
                        (9, 14, '#fff3cd', 'Alto'),
                        (14, 30, '#f8d7da', 'Muito Alto')
                    ]
                    plot_metric_with_ranges(dados_gordura_visceral, "Gordura_Visceral", "Progresso da Gordura Visceral", "Nível de Gordura Visceral", gv_ranges, ax)
                    st.pyplot(fig)
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
            
            elif tab_selecionada == "Gordura Corporal":
                dados_gordura_corporal = dados_aluno.dropna(subset=['Percentual_Gordura'])
                if not dados_gordura_corporal.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sexo = dados_aluno['Sexo'].iloc[0]
                    if sexo == "Masculino":
                        gc_ranges = [
                            (0, 6, '#f8d7da', 'Muito Baixo'),
                            (6, 14, '#d4edda', 'Normal'),
                            (14, 18, '#fff3cd', 'Moderadamente Alto'),
                            (18, 25, '#f8d7da', 'Alto'),
                            (25, 100, '#dc3545', 'Muito Alto')
                        ]
                    else:
                        gc_ranges = [
                            (0, 14, '#f8d7da', 'Muito Baixo'),
                            (14, 21, '#d4edda', 'Normal'),
                            (21, 25, '#fff3cd', 'Moderadamente Alto'),
                            (25, 32, '#f8d7da', 'Alto'),
                            (32, 100, '#dc3545', 'Muito Alto')
                        ]
                    plot_metric_with_ranges(dados_gordura_corporal, "Percentual_Gordura", "Progresso da Gordura Corporal", "Percentual de Gordura Corporal (%)", gc_ranges, ax)
                    st.pyplot(fig)
                    plt.close()
                    
                    if sexo == "Masculino":
                        st.markdown("""
                        <small>
                        * Referências de Gordura Corporal para homens:<br>
                        - Vermelho claro: Muito Baixo (< 6%)<br>
                        - Verde: Normal (6-14%)<br>
                        - Amarelo: Moderadamente Alto (14-18%)<br>
                        - Vermelho claro: Alto (18-25%)<br>
                        - Vermelho escuro: Muito Alto (> 25%)
                        </small>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <small>
                        * Referências de Gordura Corporal para mulheres:<br>
                        - Vermelho claro: Muito Baixo (< 14%)<br>
                        - Verde: Normal (14-21%)<br>
                        - Amarelo: Moderadamente Alto (21-25%)<br>
                        - Vermelho claro: Alto (25-32%)<br>
                        - Vermelho escuro: Muito Alto (> 32%)
                        </small>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Não há dados de Gordura Corporal para exibir no gráfico")
            
            
            elif tab_selecionada == "Massa Muscular":
                dados_massa_muscular = dados_aluno.dropna(subset=['Percentual_Massa_Magra'])
                if not dados_massa_muscular.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sexo = dados_aluno['Sexo'].iloc[0]
                    if sexo == "Masculino":
                        mm_ranges = [
                            (0, 33, '#f8d7da', 'Baixo'),
                            (33, 39, '#fff3cd', 'Normal'),
                            (39, 44, '#d4edda', 'Bom'),
                            (44, 100, '#28a745', 'Excelente')
                        ]
                    else:
                        mm_ranges = [
                            (0, 24, '#f8d7da', 'Baixo'),
                            (24, 30, '#fff3cd', 'Normal'),
                            (30, 35, '#d4edda', 'Bom'),
                            (35, 100, '#28a745', 'Excelente')
                        ]
                    plot_metric_with_ranges(dados_massa_muscular, "Percentual_Massa_Magra", "Progresso da Massa Muscular", "Percentual de Massa Muscular (%)", mm_ranges, ax)
                    st.pyplot(fig)
                    plt.close()
                    
                    if sexo == "Masculino":
                        st.markdown("""
                        <small>
                        * Referências de Massa Muscular para homens:<br>
                        - Vermelho claro: Baixo (< 33%)<br>
                        - Amarelo: Normal (33-39%)<br>
                        - Verde claro: Bom (39-44%)<br>
                        - Verde escuro: Excelente (> 44%)
                        </small>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <small>
                        * Referências de Massa Muscular para mulheres:<br>
                        - Vermelho claro: Baixo (< 24%)<br>
                        - Amarelo: Normal (24-30%)<br>
                        - Verde claro: Bom (30-35%)<br>
                        - Verde escuro: Excelente (> 35%)
                        </small>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Não há dados de Massa Muscular para exibir no gráfico")

    else:
        st.warning("Não há dados disponíveis para visualização.")     

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
    st.dataframe(dados_recentes[['Nome', 'Data', 'Peso', 'Altura', 'IMC']])

    fig_peso, ax_peso = plt.subplots(figsize=(10, 6))
    dados.groupby('Data')['Peso'].mean().plot(ax=ax_peso)
    ax_peso.set_title("Evolução Média do Peso dos Alunos")
    ax_peso.set_xlabel("Data")
    ax_peso.set_ylabel("Peso Médio (kg)")
    st.pyplot(fig_peso)

# Interface principal
st.title("Monitoramento de Peso e Medidas")
st.markdown("### Acompanhe o progresso físico com base em dados de peso e parâmetros da OMS")

# Menu lateral
menu = st.sidebar.selectbox("Escolha uma opção", ["Inserir Dados", "Visualizar Aluno", "Dashboard"])

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
            
            col1, col2, col3 = st.columns(3)
            with col1:
                peso_atual = dados_aluno['Peso'].iloc[-1] if not dados_aluno.empty else None
                st.metric("Peso Atual", f"{peso_atual:.1f} kg" if peso_atual is not None else "N/A")
            with col2:
                imc_atual = dados_aluno['IMC'].iloc[-1] if not dados_aluno.empty else None
                st.metric("IMC Atual", f"{imc_atual:.1f}" if imc_atual is not None else "N/A")
            with col3:
                gv_atual = dados_aluno['Gordura_Visceral'].iloc[-1] if not dados_aluno.empty else None
                st.metric("Gordura Visceral", f"{gv_atual:.1f}" if gv_atual is not None else "N/A")
            
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
                ["Progresso do Peso", "Gordura Visceral", "Massa Muscular", "Gordura Corporal"]
            )
            
            if tab_selecionada == "Progresso do Peso":
                dados_peso = dados_aluno.dropna(subset=['Peso', 'IMC'])
                if not dados_peso.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    scatter = ax.scatter(dados_peso["Data"], dados_peso["Peso"], c=dados_peso["IMC"], cmap='RdYlGn_r', s=50)
                    ax.plot(dados_peso["Data"], dados_peso["Peso"], linestyle='--', color='gray')
                    ax.set_title("Progresso do Peso e IMC", pad=20, fontsize=14)
                    ax.set_xlabel("Data", fontsize=12)
                    ax.set_ylabel("Peso (kg)", fontsize=12)
                    ax.grid(True, alpha=0.3)
                    plt.colorbar(scatter, label='IMC')
                    plt.xticks(dados_peso["Data"], dados_peso["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                    
                    st.markdown("""
                    **Recomendações da OMS para IMC:**
                    - Abaixo de 18.5: Magreza
                    - 18.5 a 24.9: Peso normal
                    - 25.0 a 29.9: Sobrepeso
                    - 30.0 a 34.9: Obesidade grau I
                    - 35.0 a 39.9: Obesidade grau II
                    - 40.0 ou mais: Obesidade grau III
                    """)
                else:
                    st.warning("Não há dados de peso para exibir no gráfico")
            
            elif tab_selecionada == "Gordura Visceral":
                dados_gordura_visceral = dados_aluno.dropna(subset=['Gordura_Visceral'])
                if not dados_gordura_visceral.empty:
                    fig_gv, ax_gv = plt.subplots(figsize=(10, 6))
                    scatter = ax_gv.scatter(dados_gordura_visceral["Data"], dados_gordura_visceral["Gordura_Visceral"], 
                                            c=dados_gordura_visceral["Gordura_Visceral"], cmap='RdYlGn_r', s=50)
                    ax_gv.plot(dados_gordura_visceral["Data"], dados_gordura_visceral["Gordura_Visceral"], linestyle='--', color='gray')
                    ax_gv.axhspan(0, 9, facecolor='green', alpha=0.1, label='Normal')
                    ax_gv.axhspan(9, 14, facecolor='yellow', alpha=0.1, label='Alto')
                    ax_gv.axhspan(14, dados_gordura_visceral["Gordura_Visceral"].max(), facecolor='red', alpha=0.1, label='Muito Alto')
                    ax_gv.set_title("Progresso da Gordura Visceral", pad=20, fontsize=14)
                    ax_gv.set_xlabel("Data", fontsize=12)
                    ax_gv.set_ylabel("Nível de Gordura Visceral", fontsize=12)
                    ax_gv.grid(True, alpha=0.3)
                    ax_gv.legend()
                    plt.colorbar(scatter, label='Gordura Visceral')
                    plt.xticks(dados_gordura_visceral["Data"], dados_gordura_visceral["Data"].dt.strftime('%d/%m/%Y'), rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig_gv)
                    plt.close()
                    
                    st.markdown("""
                    **Recomendações para Gordura Visceral:**
                    - 1 a 9: Normal
                    - 10 a 14: Alto
                    - 15 ou mais: Muito Alto
                    """)
                else:
                    st.warning("Não há dados de Gordura Visceral para exibir no gráfico")
            
            elif tab_selecionada == "Massa Muscular":
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
                

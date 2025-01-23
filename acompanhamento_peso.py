import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Acompanhamento",
    page_icon="📊",
    layout="wide"
)

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("dados_alunos.xlsx")
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Função para calcular IMC
def calcular_imc(peso, altura):
    return peso / (altura ** 2)

# Função para classificar IMC
def classificar_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso", "🔴"
    elif 18.5 <= imc < 24.9:
        return "Peso normal", "🟢"
    elif 25 <= imc < 29.9:
        return "Sobrepeso", "🟡"
    elif 30 <= imc < 34.9:
        return "Obesidade grau 1", "🔴"
    elif 35 <= imc < 39.9:
        return "Obesidade grau 2", "🔴"
    else:
        return "Obesidade grau 3", "🔴"

# Função para plotar métricas
def plot_metric(dados, x_col, y_col, title, y_label, color, additional_styling=None):
    if not dados.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dados[x_col], dados[y_col], marker="o", linewidth=2, color=color)
        
        ax.set_title(title, pad=20, fontsize=14)
        ax.set_xlabel("Data", fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(dados[x_col], dados[x_col].dt.strftime('%d/%m/%Y'), rotation=45)
        
        if additional_styling:
            additional_styling(ax)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        st.warning(f"Não há dados de {title} para exibir no gráfico")

# Função para criar o dashboard de um aluno
def criar_dashboard_aluno(dados_aluno):
    # Cabeçalho com informações do aluno
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ultima_medicao = dados_aluno.iloc[-1]
        st.subheader("Última medição")
        st.write(f"Data: {ultima_medicao['Data'].strftime('%d/%m/%Y')}")
        st.write(f"Peso: {ultima_medicao['Peso']:.1f} kg")
        
        if not pd.isna(ultima_medicao['Altura']):
            imc = calcular_imc(ultima_medicao['Peso'], ultima_medicao['Altura'])
            classificacao, indicador = classificar_imc(imc)
            st.write(f"IMC: {imc:.1f}")
            st.write(f"Classificação: {classificacao} {indicador}")
    
    with col2:
        if len(dados_aluno) >= 2:
            primeira_medicao = dados_aluno.iloc[0]
            diferenca_peso = ultima_medicao['Peso'] - primeira_medicao['Peso']
            st.subheader("Progresso")
            st.write(f"Peso inicial: {primeira_medicao['Peso']:.1f} kg")
            st.write(f"Variação de peso: {diferenca_peso:+.1f} kg")
    
    with col3:
        if not pd.isna(ultima_medicao['Meta_Peso']):
            st.subheader("Meta")
            st.write(f"Meta de peso: {ultima_medicao['Meta_Peso']:.1f} kg")
            diferenca_meta = ultima_medicao['Meta_Peso'] - ultima_medicao['Peso']
            st.write(f"Faltam: {abs(diferenca_meta):.1f} kg")

    # Seleção de gráficos
    tab_selecionada = st.radio(
        "Selecione o gráfico:",
        ["Progresso do Peso", "Medidas Corporais", "Gordura Visceral", "Massa Muscular", "Gordura Corporal"]
    )
    
    if tab_selecionada == "Progresso do Peso":
        plot_metric(dados_aluno, "Data", "Peso", "Progresso do Peso", "Peso (kg)", '#3498DB')

    elif tab_selecionada == "Medidas Corporais":
        dados_medidas = dados_aluno.dropna(subset=['Cintura', 'Quadril'])
        if not dados_medidas.empty:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            ax1.plot(dados_medidas["Data"], dados_medidas["Cintura"], marker="o", linewidth=2, color='#9B59B6')
            ax2.plot(dados_medidas["Data"], dados_medidas["Quadril"], marker="o", linewidth=2, color='#F1C40F')
            
            ax1.set_title("Medida da Cintura")
            ax2.set_title("Medida do Quadril")
            
            for ax in [ax1, ax2]:
                ax.set_xlabel("Data")
                ax.set_ylabel("Medida (cm)")
                ax.grid(True, alpha=0.3)
                ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("Não há dados de medidas suficientes para gerar os gráficos")

    elif tab_selecionada == "Gordura Visceral":
        dados_gordura_visceral = dados_aluno.dropna(subset=['Gordura_Visceral'])
        
        def style_gordura_visceral(ax):
            ax.axhspan(0, 9, facecolor='green', alpha=0.3, label='Normal')
            ax.axhspan(9, 14, facecolor='yellow', alpha=0.3, label='Alto')
            ax.axhspan(14, 30, facecolor='red', alpha=0.3, label='Muito Alto')
            ax.legend()
        
        plot_metric(dados_gordura_visceral, "Data", "Gordura_Visceral", 
                    "Progresso da Gordura Visceral", "Nível de Gordura Visceral", 
                    '#2E86C1', additional_styling=style_gordura_visceral)
        
        st.markdown("""
        <small>
        * Referências de Gordura Visceral:<br>
        - Verde: Normal (1-9)<br>
        - Amarelo: Alto (10-14)<br>
        - Vermelho: Muito Alto (15+)
        </small>
        """, unsafe_allow_html=True)

    elif tab_selecionada == "Massa Muscular":
        dados_massa_muscular = dados_aluno.dropna(subset=['Percentual_Massa_Magra'])
        plot_metric(dados_massa_muscular, "Data", "Percentual_Massa_Magra", 
                    "Progresso da Massa Muscular", "Percentual de Massa Muscular", '#27AE60')

    elif tab_selecionada == "Gordura Corporal":
        dados_gordura_corporal = dados_aluno.dropna(subset=['Percentual_Gordura'])
        plot_metric(dados_gordura_corporal, "Data", "Percentual_Gordura", 
                    "Progresso da Gordura Corporal", "Percentual de Gordura Corporal", '#E74C3C')

# Função principal
def main():
    st.title("Dashboard de Acompanhamento de Alunos")
    
    menu = st.sidebar.selectbox("Menu", ["Visualizar Aluno", "Dashboard Geral"])
    
    dados = load_data()
    
    if menu == "Visualizar Aluno":
        if not dados.empty:
            alunos = dados["Nome"].unique()
            aluno_selecionado = st.selectbox("Selecione um aluno", alunos)
            
            if aluno_selecionado:
                dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")
                criar_dashboard_aluno(dados_aluno)
            else:
                st.warning("Selecione um aluno para visualizar os dados.")
        else:
            st.warning("Não há dados disponíveis para visualização.")
    
    elif menu == "Dashboard Geral":
        st.write("Dashboard Geral - Em desenvolvimento")

if __name__ == "__main__":
    main()

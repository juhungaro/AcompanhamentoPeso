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
        altura = st.number_input("Altura (em metros)", format="%.1f", min_value=0.0, max_value=3.0, step=0.01)
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
            
            # Criar duas colunas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Resultado individual
                classificacao, nivel = get_imc_classification(imc_atual)
                
                if nivel == "success":
                    st.success(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
                elif nivel == "warning":
                    st.warning(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
                else:
                    st.error(f"IMC: {imc_atual:.1f} - Classificação: {classificacao}")
            
            with col2:
                # Tabela de classificação
                st.markdown("**Tabela de Classificação IMC (OMS)**")
                
                classificacao_imc = pd.DataFrame({
                    'IMC': ['Menor que 18,5', '18,5 a 24,9', '25,0 a 29,9', '30,0 a 34,9', '35,0 a 39,9', 'Maior que 40,0'],
                    'Classificação': ['Magreza', 'Normal', 'Sobrepeso', 'Obesidade grau I', 'Obesidade grau II', 'Obesidade grau III'],
                    'Risco': ['Elevado', 'Normal', 'Elevado', 'Muito elevado', 'Muitíssimo elevado', 'Obesidade mórbida']
                })
                
                # Estilizar a tabela
                def highlight_row(row):
                    imc_valor = float(imc_atual)
                    
                    if imc_valor < 18.5 and row.name == 0:
                        return ['background-color: #fff3cd'] * len(row)
                    elif 18.5 <= imc_valor < 25 and row.name == 1:
                        return ['background-color: #d4edda'] * len(row)
                    elif 25 <= imc_valor < 30 and row.name == 2:
                        return ['background-color: #fff3cd'] * len(row)
                    elif 30 <= imc_valor < 35 and row.name == 3:
                        return ['background-color: #f8d7da'] * len(row)
                    elif 35 <= imc_valor < 40 and row.name == 4:
                        return ['background-color: #f8d7da'] * len(row)
                    elif imc_valor >= 40 and row.name == 5:
                        return ['background-color: #f8d7da'] * len(row)
                    return [''] * len(row)
                
                st.dataframe(
                    classificacao_imc.style.apply(highlight_row, axis=1),
                    hide_index=True,
                    use_container_width=True
                )
                
                # Nota explicativa
                st.markdown("""
                <small>* A linha destacada corresponde à sua classificação atual.</small>
                """, unsafe_allow_html=True)

            
            # Gráficos
            tab1, tab2 = st.tabs(["Progresso do Peso", "Medidas Corporais"])
            
            with tab1:
                # Remover dados nulos
                dados_peso = dados_aluno.dropna(subset=['Peso'])
                
                if not dados_peso.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Calcular os limites de peso baseados no IMC para a altura atual
                    altura_atual = dados_aluno['Altura'].iloc[-1]
                    
                    # Definir limites de IMC e cores correspondentes
                    imc_ranges = [
                        (0, 18.5, '#fff3cd', 'Magreza'),
                        (18.5, 24.9, '#d4edda', 'Normal'),
                        (25, 29.9, '#fff3cd', 'Sobrepeso'),
                        (30, 34.9, '#f8d7da', 'Obesidade I'),
                        (35, 39.9, '#f8d7da', 'Obesidade II'),
                        (40, 50, '#f8d7da', 'Obesidade III')
                    ]
                    
                    # Calcular e plotar as áreas de referência
                    y_min = dados_peso['Peso'].min() * 0.8  # 20% abaixo do peso mínimo
                    y_max = dados_peso['Peso'].max() * 1.2  # 20% acima do peso máximo
                    
                    # Plotar as áreas de referência
                    for imc_min, imc_max, color, label in imc_ranges:
                        peso_min = (imc_min * (altura_atual ** 2))
                        peso_max = (imc_max * (altura_atual ** 2))
                        ax.axhspan(peso_min, peso_max, color=color, alpha=0.3, label=f'Faixa {label}')
                    
                    # Plotar linha do peso
                    ax.plot(dados_peso["Data"], dados_peso["Peso"], 
                           marker="o", linewidth=2, color='#2E86C1', 
                           label='Peso atual', zorder=5)
                    
                    # Adicionar valores nos pontos
                    for x, y in zip(dados_peso["Data"], dados_peso["Peso"]):
                        ax.annotate(f'{y:.1f}', 
                                  (x, y), 
                                  textcoords="offset points", 
                                  xytext=(0,10), 
                                  ha='center',
                                  fontsize=9,
                                  zorder=6)
                    
                    # Configurações do gráfico
                    ax.set_title("Progresso do Peso com Faixas de Referência IMC", pad=20, fontsize=14)
                    ax.set_xlabel("Data", fontsize=12)
                    ax.set_ylabel("Peso (kg)", fontsize=12)
                    ax.grid(True, alpha=0.3, zorder=1)
                    
                    # Ajustar limites do eixo y
                    ax.set_ylim(y_min, y_max)
                    
                    # Ajustar datas no eixo x
                    dates = dados_peso["Data"]
                    plt.xticks(dates, dates.dt.strftime('%d/%m/%Y'), rotation=45)
                    
                    # Adicionar legenda
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    
                    # Ajustar layout para acomodar a legenda
                    plt.tight_layout()
                    
                    # Exibir o gráfico
                    st.pyplot(fig)
                    plt.close()
                    
                    # Adicionar nota explicativa
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
                # Remover dados nulos de cintura e quadril
                dados_medidas = dados_aluno.dropna(subset=['Cintura', 'Quadril'])
                
                if not dados_medidas.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Definir faixas de referência baseadas no sexo
                    sexo_atual = dados_aluno['Sexo'].iloc[0]
                    if sexo_atual == "Masculino":
                        cintura_ranges = [
                            (0, 94, '#d4edda', 'Normal'),
                            (94, 102, '#fff3cd', 'Risco Aumentado'),
                            (102, 200, '#f8d7da', 'Risco Alto')
                        ]
                    else:  # Feminino
                        cintura_ranges = [
                            (0, 80, '#d4edda', 'Normal'),
                            (80, 88, '#fff3cd', 'Risco Aumentado'),
                            (88, 200, '#f8d7da', 'Risco Alto')
                        ]
                    
                    # Calcular limites do gráfico
                    y_min = min(dados_medidas['Cintura'].min(), dados_medidas['Quadril'].min()) * 0.9
                    y_max = max(dados_medidas['Cintura'].max(), dados_medidas['Quadril'].max()) * 1.1
                    
                    # Plotar áreas de referência para cintura
                    for c_min, c_max, color, label in cintura_ranges:
                        ax.axhspan(c_min, c_max, color=color, alpha=0.3, 
                                 label=f'Cintura: {label}')
                    
                    # Plotar linhas de medidas
                    ax.plot(dados_medidas["Data"], dados_medidas["Cintura"], 
                           marker="o", label="Cintura", color='#E74C3C',
                           linewidth=2, zorder=5)
                    
                    ax.plot(dados_medidas["Data"], dados_medidas["Quadril"], 
                           marker="o", label="Quadril", color='#8E44AD',
                           linewidth=2, zorder=5)
                    
                    # Adicionar valores nos pontos
                    for x, y in zip(dados_medidas["Data"], dados_medidas["Cintura"]):
                        ax.annotate(f'{y:.1f}', 
                                  (x, y), 
                                  textcoords="offset points", 
                                  xytext=(0,10), 
                                  ha='center',
                                  fontsize=9,
                                  zorder=6)
                    
                    for x, y in zip(dados_medidas["Data"], dados_medidas["Quadril"]):
                        ax.annotate(f'{y:.1f}', 
                                  (x, y), 
                                  textcoords="offset points", 
                                  xytext=(0,-15), 
                                  ha='center',
                                  fontsize=9,
                                  zorder=6)
                    
                    # Configurações do gráfico
                    ax.set_title(f"Medidas Corporais com Referências OMS ({sexo_atual})", 
                               pad=20, fontsize=14)
                    ax.set_xlabel("Data", fontsize=12)
                    ax.set_ylabel("Centímetros", fontsize=12)
                    ax.grid(True, alpha=0.3, zorder=1)
                    
                    # Ajustar limites do eixo y
                    ax.set_ylim(y_min, y_max)
                    
                    # Ajustar datas no eixo x
                    dates = dados_medidas["Data"]
                    plt.xticks(dates, dates.dt.strftime('%d/%m/%Y'), rotation=45)
                    
                    # Adicionar legenda
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                    
                    # Ajustar layout
                    plt.tight_layout()
                    
                    # Exibir o gráfico
                    st.pyplot(fig)
                    plt.close()
                    
                    # Adicionar nota explicativa
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
                    st.warning("Não há dados de medidas suficientes para gerar o gráfico")

            
            # Tabela de dados
            st.subheader("Histórico de Medições")
            dados_display = dados_aluno.sort_values("Data", ascending=False).copy()
            dados_display["Data"] = dados_display["Data"].dt.strftime('%d/%m/%Y')
            st.dataframe(dados_display, use_container_width=True)
            
            # Botão de download
            csv = dados_aluno.to_csv(index=False)
            st.download_button(
                label="📥 Download dos dados",
                data=csv,
                file_name=f"dados_{aluno_selecionado}.csv",
                mime="text/csv"
            )
            
except Exception as e:
    st.error(f"Ocorreu um erro ao carregar os dados: {str(e)}")

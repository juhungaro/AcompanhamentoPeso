# Separar o código em funções para melhor organização
def load_data():
    try:
        return pd.read_csv("dados_alunos.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

def save_data(dados_aluno):
    dados_aluno.to_csv("dados_alunos.csv", index=False)

def calculate_metrics(peso, altura, cintura, quadril):
    imc = round(peso / (altura ** 2), 2) if altura > 0 and peso > 0 else None
    rcq = round(cintura / quadril, 2) if quadril > 0 and cintura > 0 else None
    return imc, rcq

def validate_inputs(nome, altura, peso):
    if not nome:
        return False, "Nome é obrigatório"
    if altura <= 0:
        return False, "Altura deve ser maior que zero"
    if peso <= 0:
        return False, "Peso deve ser maior que zero"
    return True, ""

def plot_weight_progress(dados_aluno):
    fig = plt.figure(figsize=(10, 6))
    plt.style.use('seaborn')  # Melhor estilo visual
    
    plt.plot(dados_aluno["Data"], dados_aluno["Peso"], 
             marker="o", linewidth=2, markersize=8)
    
    # Formatação do gráfico
    plt.title("Progresso do Peso", fontsize=14, pad=20)
    plt.xlabel("Data", fontsize=12)
    plt.ylabel("Peso (kg)", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    return fig

@st.cache_data
def load_cached_data():
    return load_data()

try:
    dados = load_cached_data()
    if dados.empty:
        st.info("Nenhum dado encontrado. Insira os dados para começar!")
        st.stop()
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    st.stop()

def add_filters(dados):
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", 
                                   min(dados["Data"]))
    with col2:
        data_fim = st.date_input("Data Final", 
                                max(dados["Data"]))
    return data_inicio, data_fim

def show_statistics(dados_aluno):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peso Inicial", f"{dados_aluno['Peso'].iloc[0]:.1f} kg")
    with col2:
        st.metric("Peso Atual", f"{dados_aluno['Peso'].iloc[-1]:.1f} kg")
    with col3:
        diferenca = dados_aluno['Peso'].iloc[-1] - dados_aluno['Peso'].iloc[0]
        st.metric("Variação", f"{diferenca:.1f} kg")

def get_imc_feedback(imc):
    feedbacks = {
        (0, 18.5): ("Magreza", "warning", "Consulte um especialista"),
        (18.5, 24.9): ("Peso normal", "success", "Continue assim!"),
        (25, 29.9): ("Sobrepeso", "warning", "Mantenha hábitos saudáveis"),
        (30, 34.9): ("Obesidade Grau I", "error", "Acompanhamento recomendado"),
        (35, 39.9): ("Obesidade Grau II", "error", "Procure ajuda especializada"),
        (40, float('inf')): ("Obesidade Grau III", "error", "Intervenção necessária")
    }
    
    for (min_val, max_val), (status, level, message) in feedbacks.items():
        if min_val <= imc < max_val:
            return status, level, message

def add_export_option(dados_aluno):
    if st.button("Exportar Dados"):
        csv = dados_aluno.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="dados_aluno.csv",
            mime="text/csv"
        )


import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# ---- Configurações básicas da aplicação
st.title("Monitoramento de Peso e Medidas")
st.sidebar.title("Menu")
st.markdown("### Acompanhe o progresso físico com base em dados de peso, medidas e parâmetros da OMS")

# -----------------------------------------------------------
# ---- Criando espaço para entrada de dados
st.sidebar.header("Inserir dados do aluno")

# Entrada dos dados do aluno
nome = st.sidebar.text_input("Nome do aluno")
sexo = st.sidebar.selectbox("Sexo", ["Masculino", "Feminino"])
altura = st.sidebar.number_input("Altura (em metros)", format="%.2f")
peso = st.sidebar.number_input("Peso atual (em kg)", format="%.1f")
cintura = st.sidebar.number_input("Circunferência da Cintura (em cm)", format="%.1f")
quadril = st.sidebar.number_input("Circunferência do Quadril (em cm)", format="%.1f")
data = st.sidebar.date_input("Data da medição", value=datetime.date.today())

# Botão para gravar dados
if st.sidebar.button("Salvar Dados"):
    if nome and altura > 0 and peso > 0:
        # Criação ou carregamento da base de dados
        try:
            dados = pd.read_csv("dados_alunos.csv")
        except FileNotFoundError:
            dados = pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

        # Cálculos
        imc = peso / (altura ** 2) if altura > 0 else 0
        razao_cq = cintura / quadril if quadril > 0 else 0

        # Novo registro
        novo_dado = pd.DataFrame({
            "Nome": [nome],
            "Sexo": [sexo],
            "Data": [data],
            "Altura": [altura],
            "Peso": [peso],
            "Cintura": [cintura],
            "Quadril": [quadril],
            "IMC": [imc],
            "C/Q": [razao_cq]
        })

        # Atualizar base de dados e salvar
        dados = pd.concat([dados, novo_dado], ignore_index=True)
        dados.to_csv("dados_alunos.csv", index=False)
        st.sidebar.success("Dados salvos com sucesso!")
    else:
        st.sidebar.error("Todos os campos devem ser preenchidos corretamente!")

# -----------------------------------------------------------
# ---- Exibição de dados e gráficos
# Importação da base de dados
try:
    dados = pd.read_csv("dados_alunos.csv")

    # Seleção de aluno para análise
    alunos = dados["Nome"].unique()
    aluno_selecionado = st.selectbox("Selecione um aluno para visualizar os dados", alunos)

    if aluno_selecionado:
        # Filtrar dados do aluno
        dados_aluno = dados[dados["Nome"] == aluno_selecionado]

        # Exibir tabela de dados
        st.subheader(f"Dados de {aluno_selecionado}")
        st.dataframe(dados_aluno)

        # Exibir gráficos de progresso
        st.subheader("Progresso ao longo do tempo")

        # Plotar gráfico de peso com faixa saudável de peso
        fig, ax = plt.subplots()
        # Adicionar faixa de peso ideal (área sombreada)
        altura_atual = dados_aluno["Altura"].iloc[-1]  # Garantindo altura do último registro
        peso_minimo = 18.5 * (altura_atual ** 2)
        peso_maximo = 24.9 * (altura_atual ** 2)
        ax.axhspan(peso_minimo, peso_maximo, color="green", alpha=0.2, label="Faixa de Peso Ideal")

        # Plotar o progresso do peso
        ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")
        ax.set_title("Progresso do Peso com Faixa Ideal")
        ax.set_xlabel("Data")
        ax.set_ylabel("Peso (kg)")
        ax.legend()
        st.pyplot(fig)

        # Plotar gráfico de medidas (cintura e quadril) com faixas ideais para cintura
        fig, ax = plt.subplots()

        # Faixas para a circunferência da cintura conforme o sexo
        if sexo == "Masculino":
            cintura_max = 94
            cintura_alerta = 102
        elif sexo == "Feminino":
            cintura_max = 80
            cintura_alerta = 88

        # Adicionar as faixas de cintura ao gráfico
        ax.axhspan(0, cintura_max, color="green", alpha=0.2, label="Faixa Saudável (Cintura)")
        ax.axhspan(cintura_max, cintura_alerta, color="yellow", alpha=0.2, label="Risco Moderado (Cintura)")
        ax.axhspan(cintura_alerta, max(dados_aluno["Cintura"].max() + 10, cintura_alerta + 10), color="red", alpha=0.2, label="Risco Alto (Cintura)")

        # Plotar o progresso das medidas
        ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
        ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")
        ax.set_title("Progresso das Medidas com Faixas Ideais")
        ax.set_xlabel("Data")
        ax.set_ylabel("Medidas (cm)")
        ax.legend()
        st.pyplot(fig)

        # Feedback quanto aos parâmetros
        st.subheader("Feedback sobre a saúde")
        imc_atual = dados_aluno["IMC"].iloc[-1]
        razao_cq_atual = dados_aluno["C/Q"].iloc[-1]

        if imc_atual < 18.5:
            st.warning("IMC indica magreza (abaixo de 18,5)")
        elif 18.5 <= imc_atual < 24.9:
            st.success("IMC dentro da faixa saudável (18,5 a 24,9).")
        elif 25 <= imc_atual < 29.9:
            st.warning("IMC indica sobrepeso (25 a 29,9).")
        else:
            st.error("IMC indica obesidade (acima de 30).")

        # Faixas da RCQ de acordo com a OMS
        if sexo == "Masculino":
            if razao_cq_atual <= 0.90:
                st.success("A relação cintura-quadril está dentro do padrão saudável (Baixo Risco).")
            elif 0.91 <= razao_cq_atual < 1.00:
                st.warning("Relação cintura-quadril indica Moderado Risco.")
            else:
                st.error("Relação cintura-quadril indica Alto Risco.")
        elif sexo == "Feminino":
            if razao_cq_atual <= 0.85:
                st.success("A relação cintura-quadril está dentro do padrão saudável (Baixo Risco).")
            elif 0.86 <= razao_cq_atual < 0.95:
                st.warning("Relação cintura-quadril indica Moderado Risco.")
            else:
                st.error("Relação cintura-quadril indica Alto Risco.")

except FileNotFoundError:
    st.warning("Nenhum dado encontrado. Por favor, insira os dados de um aluno para começar.")

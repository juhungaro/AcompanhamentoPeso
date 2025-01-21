import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

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
altura = st.sidebar.number_input("Altura (em metros)", format="%.2f", min_value=0.1, step=0.01)
peso = st.sidebar.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, step=0.1)
cintura = st.sidebar.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1)
quadril = st.sidebar.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1)
data = st.sidebar.date_input("Data da medição", value=dt.date.today())

# Botão para salvar os dados
if st.sidebar.button("Salvar Dados"):
    if nome and altura > 0 and peso > 0:  # Garantir valores válidos
        # Tentar carregar a base de dados existente
        try:
            dados = pd.read_csv("dados_alunos.csv")
        except FileNotFoundError:
            dados = pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

        # Calcular IMC e RCQ
        imc = round(peso / (altura ** 2), 2)
        razao_cq = round(cintura / quadril, 2) if quadril > 0 else None

        # Criar uma nova linha com os dados inseridos
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

        # Atualizar e salvar os dados
        dados = pd.concat([dados, novo_dado], ignore_index=True)
        dados.to_csv("dados_alunos.csv", index=False)
        st.sidebar.success("Dados salvos com sucesso!")
    else:
        st.sidebar.error("Preencha todos os campos corretamente!")

# -----------------------------------------------------------
# ---- Visualização de dados e gráficos
try:
    dados = pd.read_csv("dados_alunos.csv")

    # Converter valores das colunas para os formatos apropriados
    dados["Data"] = pd.to_datetime(dados["Data"], errors="coerce")  # Converter as datas
    dados.dropna(subset=["Data", "Peso", "Cintura", "Quadril"], inplace=True)

    # Selecionar aluno para visualização
    alunos = dados["Nome"].unique()
    aluno_selecionado = st.selectbox("Selecione um aluno para visualizar os dados", alunos)

    if aluno_selecionado:
        dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")

        st.subheader(f"Dados de {aluno_selecionado}")
        st.dataframe(dados_aluno)

        # --- Gráfico do Peso ---
        st.subheader("Progresso do Peso")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotar progresso do peso
        ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Peso"]):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center")

        ax.set_title("Progresso do Peso")
        ax.set_xlabel("Data")
        ax.set_ylabel("Peso (kg)")
        ax.grid(alpha=0.4, linestyle="--")
        ax.legend(["Peso (kg)"], loc="upper right")
        st.pyplot(fig)

        # --- Gráfico de Medidas ---
        st.subheader("Progresso das Medidas")
        if not dados_aluno["Cintura"].isnull().all() and not dados_aluno["Quadril"].isnull().all():
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plotar progresso de cintura e quadril
            ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
            ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")

            # Anotações
            for x, y in zip(dados_aluno["Data"], dados_aluno["Cintura"]):
                ax.annotate(f"{y:.1f}", (x, y + 1.5), textcoords="offset points", ha="center")
            for x, y in zip(dados_aluno["Data"], dados_aluno["Quadril"]):
                ax.annotate(f"{y:.1f}", (x, y - 1.5), textcoords="offset points", ha="center")

            ax.set_title("Progresso de Cintura e Quadril")
            ax.set_xlabel("Data")
            ax.set_ylabel("Medidas (cm)")
            ax.grid(alpha=0.4, linestyle="--")
            ax.legend(["Cintura (cm)", "Quadril (cm)"], loc="upper right")
            st.pyplot(fig)
        else:
            st.warning("Não há dados suficientes para as medidas de cintura e quadril.")

        # --- Feedback do IMC ---
        st.subheader("Classificação do IMC")
        altura_atual = dados_aluno["Altura"].iloc[-1]
        peso_atual = dados_aluno["Peso"].iloc[-1]
        if altura_atual > 0 and peso_atual > 0:
            imc_atual = round(peso_atual / (altura_atual ** 2), 2)
            st.write(f"**IMC Atual:** {imc_atual:.1f}")
            if imc_atual < 18.5:
                st.warning("Classificação: Magreza (IMC < 18.5). Consulte um especialista.")
            elif 18.5 <= imc_atual < 24.9:
                st.success("Classificação: Peso normal (IMC 18.5 - 24.9). Continue assim!")
            elif 25 <= imc_atual < 29.9:
                st.warning("Classificação: Sobrepeso (IMC 25 - 29.9). Cuide-se com hábitos saudáveis.")
            elif 30 <= imc_atual < 34.9:
                st.error("Classificação: Obesidade Grau I (IMC 30 - 34.9). Acompanhamento recomendado.")
            elif 35 <= imc_atual < 39.9:
                st.error("Classificação: Obesidade Grau II (IMC 35 - 39.9). Procure ajuda especializada.")
            else:
                st.error("Classificação: Obesidade Grau III (IMC ≥ 40). Intervenção necessária.")
        else:
            st.error("Dados insuficientes para calcular o IMC. Verifique a altura e o peso.")

except FileNotFoundError:
    st.warning("Nenhum dado encontrado. Por favor, insira os dados de um aluno para começar!")

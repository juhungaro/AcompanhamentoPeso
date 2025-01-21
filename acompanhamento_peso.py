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
    if nome and altura > 0 and peso > 0:
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
    dados["Data"] = pd.to_datetime(dados["Data"], errors="coerce")
    dados.dropna(subset=["Data", "Peso", "Cintura", "Quadril"], inplace=True)

    # Selecionar aluno para visualização
    alunos = dados["Nome"].unique()
    aluno_selecionado = st.selectbox("Selecione um aluno para visualizar os dados", alunos)

    if aluno_selecionado:
        dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")

        st.subheader(f"Dados de {aluno_selecionado}")
        st.dataframe(dados_aluno)

        # --- Gráfico do Peso ---
        st.subheader("Progresso do Peso com Faixa Ideal")
        fig, ax = plt.subplots(figsize=(10, 5))
        altura_atual = dados_aluno["Altura"].iloc[-1]

        # Calcular faixa de peso ideal
        peso_minimo = round(18.5 * (altura_atual ** 2), 2)
        peso_maximo = round(24.9 * (altura_atual ** 2), 2)

        # Faixa de peso saudável
        ax.axhspan(peso_minimo, peso_maximo, color="green", alpha=0.2, label="Faixa de Peso Ideal")

        # Configurar limites do gráfico no eixo Y
        peso_min = min(peso_minimo, dados_aluno["Peso"].min()) - 2
        peso_max = max(peso_maximo, dados_aluno["Peso"].max()) + 2
        ax.set_ylim(peso_min, peso_max)

        # Progresso do peso
        ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Peso"]):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center")

        # Configurar título e rótulos
        ax.set_title("Progresso do Peso com Faixa Ideal")
        ax.set_xlabel("Data")
        ax.set_ylabel("Peso (kg)")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        plt.tight_layout()
        st.pyplot(fig)

        # --- Gráfico de Medidas ---
        st.subheader("Progresso das Medidas com Faixa de Risco")
        fig, ax = plt.subplots(figsize=(10, 5))
        sexo_aluno = dados_aluno["Sexo"].iloc[-1]

        # Faixas de risco baseadas no sexo
        cintura_max = 94 if sexo_aluno == "Masculino" else 80
        cintura_alerta = 102 if sexo_aluno == "Masculino" else 88

        # Adicionar faixas de risco
        ax.axhspan(0, cintura_max, color="green", alpha=0.2, label="Faixa Saudável (Cintura)")
        ax.axhspan(cintura_max, cintura_alerta, color="yellow", alpha=0.2, label="Risco Moderado (Cintura)")
        ax.axhspan(cintura_alerta, dados_aluno["Cintura"].max() + 10, color="red", alpha=0.2, label="Risco Alto (Cintura)")

        # Progresso de medidas
        ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
        ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Cintura"]):
            ax.annotate(f"{y:.1f}", (x, y + 2), textcoords="offset points", ha="center")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Quadril"]):
            ax.annotate(f"{y:.1f}", (x, y - 2), textcoords="offset points", ha="center")

        # Configuração gráfica
        ax.set_title("Progresso das Medidas")
        ax.set_xlabel("Data")
        ax.set_ylabel("Medidas (cm)")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        plt.tight_layout()
        st.pyplot(fig)

        # --- Feedback do IMC e RCQ ---
        st.subheader("Feedback sobre Saúde")

        # Cálculo do IMC
        imc_atual = dados_aluno["IMC"].iloc[-1]
        st.write(f"**IMC atual:** {imc_atual}")
        if imc_atual < 18.5:
            st.warning("Classificação: Magreza")
        elif 18.5 <= imc_atual < 24.9:
            st.success("Classificação: Peso normal")
        elif 24.9 <= imc_atual < 29.9:
            st.warning("Classificação: Sobrepeso")
        elif 29.9 <= imc_atual < 34.9:
            st.error("Classificação: Obesidade grau I")
        elif 34.9 <= imc_atual < 39.9:
            st.error("Classificação: Obesidade grau II")
        else:
            st.error("Classificação: Obesidade grau III")

        # Feedback do RCQ
        razao_cq = dados_aluno["C/Q"].iloc[-1]
        st.write(f"**Relação cintura-quadril (RCQ):** {razao_cq}")
        if sexo_aluno == "Masculino":
            if razao_cq <= 0.90:
                st.success("RCQ dentro da faixa saudável.")
            elif razao_cq <= 1.00:
                st.warning("RCQ com risco moderado.")
            else:
                st.error("RCQ com risco alto.")
        else:
            if razao_cq <= 0.85:
                st.success("RCQ dentro da faixa saudável.")
            elif razao_cq <= 0.95:
                st.warning("RCQ com risco moderado.")
            else:
                st.error("RCQ com risco alto.")
except FileNotFoundError:
    st.warning("Nenhum dado encontrado. Por favor, insira os dados de um aluno para começar.")

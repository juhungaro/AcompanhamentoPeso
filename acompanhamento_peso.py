import streamlit as st
import pandas as pd
import datetime as dt
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
altura = st.sidebar.number_input("Altura (em metros)", format="%.2f", min_value=0.1, step=0.01)
peso = st.sidebar.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, step=0.1)
cintura = st.sidebar.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1)
quadril = st.sidebar.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1)
data = st.sidebar.date_input("Data da medição", value=dt.date.today())

# Botão para salvar os dados
if st.sidebar.button("Salvar Dados"):
    if nome and altura > 0 and peso > 0:
        # Fazer carregamento ou criar a base de dados
        try:
            dados = pd.read_csv("dados_alunos.csv")
        except FileNotFoundError:
            dados = pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

        # Cálculos de IMC e RCQ
        imc = round(peso / (altura ** 2), 2)
        razao_cq = round(cintura / quadril, 2) if quadril > 0 else None

        # Adicionar novos dados
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

        # Atualizar base e salvar
        dados = pd.concat([dados, novo_dado], ignore_index=True)
        dados.to_csv("dados_alunos.csv", index=False)
        st.sidebar.success("Dados salvos com sucesso!")
    else:
        st.sidebar.error("Preencha todos os campos corretamente!")

# -----------------------------------------------------------
# ---- Visualização de dados e gráficos
try:
    dados = pd.read_csv("dados_alunos.csv")

    # Garantir conversão apropriada de colunas
    dados["Data"] = pd.to_datetime(dados["Data"], errors="coerce")
    dados.dropna(subset=["Data", "Peso", "Cintura", "Quadril"], inplace=True)

    # Escolher aluno
    alunos = dados["Nome"].unique()
    aluno_selecionado = st.selectbox("Selecione um aluno para visualizar os dados", alunos)

    if aluno_selecionado:
        dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values("Data")

        st.subheader(f"Dados de {aluno_selecionado}")
        st.dataframe(dados_aluno)

        # Gráfico de peso
        st.subheader("Progresso do Peso com Faixa Ideal")
        fig, ax = plt.subplots(figsize=(10, 5))
        altura_atual = dados_aluno["Altura"].iloc[-1]
        peso_minimo = round(18.5 * (altura_atual ** 2), 2)
        peso_maximo = round(24.9 * (altura_atual ** 2), 2)

        # Faixa de peso ideal
        ax.axhspan(peso_minimo, peso_maximo, color="green", alpha=0.2, label="Faixa de Peso Ideal")

        # Configurar escala do eixo Y ajustada ao peso
        peso_min = min(peso_minimo, dados_aluno["Peso"].min()) - 2
        peso_max = max(peso_maximo, dados_aluno["Peso"].max()) + 2
        ax.set_ylim(peso_min, peso_max)

        # Progresso do peso
        ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Peso"]):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center")

        # Personalizar gráfico
        ax.set_title("Progresso do Peso com Faixa Ideal")
        ax.set_xlabel("Data")
        ax.set_ylabel("Peso (kg)")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))  # Legenda fora do gráfico
        ax.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)

        # Gráfico de medidas
        st.subheader("Progresso das Medidas com Faixa de Risco")
        fig, ax = plt.subplots(figsize=(10, 5))

        # Faixas de risco para cintura
        cintura_max = 94 if dados_aluno["Sexo"].iloc[-1] == "Masculino" else 80
        cintura_alerta = 102 if dados_aluno["Sexo"].iloc[-1] == "Masculino" else 88

        ax.axhspan(0, cintura_max, color="green", alpha=0.2, label="Faixa Saudável")
        ax.axhspan(cintura_max, cintura_alerta, color="yellow", alpha=0.2, label="Risco Moderado")
        ax.axhspan(cintura_alerta, dados_aluno["Cintura"].max() + 10, color="red", alpha=0.2, label="Risco Alto")

        # Progresso de medidas
        ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
        ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Cintura"]):
            ax.annotate(f"{y:.1f}", (x, y + 1.5), textcoords="offset points", ha="center")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Quadril"]):
            ax.annotate(f"{y:.1f}", (x, y - 2.5), textcoords="offset points", ha="center")

        # Personalizar gráfico
        ax.set_title("Progresso das Medidas")
        ax.set_xlabel("Data")
        ax.set_ylabel("Medidas (cm)")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))  # Legenda fora do gráfico
        ax.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)

        # Feedback sobre IMC e RCQ
        st.subheader("Feedback sobre a Saúde")

        # IMC Feedback
        imc_atual = dados_aluno["IMC"].iloc[-1]
        st.write(f"IMC atual: {imc_atual:.1f}")
        if imc_atual < 18.5:
            st.warning("Baixo peso.")
        elif 18.5 <= imc_atual < 24.9:
            st.success("Peso normal.")
        elif 24.9 <= imc_atual < 29.9:
            st.warning("Sobrepeso.")
        elif 29.9 <= imc_atual < 34.9:
            st.error("Obesidade grau I.")
        elif 34.9 <= imc_atual < 39.9:
            st.error("Obesidade grau II.")
        else:
            st.error("Obesidade grau III.")

        # RCQ Feedback
        razao_cq_atual = dados_aluno["C/Q"].iloc[-1]
        st.write(f"Relação Cintura-Quadril atual (RCQ): {razao_cq_atual:.2f}")
        if dados_aluno["Sexo"].iloc[-1] == "Masculino":
            if razao_cq_atual <= 0.90:
                st.success("RCQ está dentro do padrão saudável (Baixo Risco).")
            elif 0.91 <= razao_cq_atual < 1.00:
                st.warning("RCQ indica Moderado Risco.")
            else:
                st.error("RCQ indica Alto Risco.")
        elif dados_aluno["Sexo"].iloc[-1] == "Feminino":
            if razao_cq_atual <= 0.85:
                st.success("RCQ está dentro do padrão saudável (Baixo Risco).")
            elif 0.86 <= razao_cq_atual < 0.95:
                st.warning("RCQ indica Moderado Risco.")
            else:
                st.error("RCQ indica Alto Risco.")
except FileNotFoundError:
    st.warning("Nenhum dado encontrado. Por favor, insira os dados de um aluno para começar.")

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
        st.subheader("Progresso do Peso com Faixa Ideal")
        fig, ax = plt.subplots(figsize=(10, 6))
        altura_atual = dados_aluno["Altura"].iloc[-1]

        # Calcular faixa de peso ideal
        peso_minimo = round(18.5 * (altura_atual ** 2), 2)
        peso_maximo = round(24.9 * (altura_atual ** 2), 2)

        # Adicionar faixa de peso saudável
        ax.axhspan(peso_minimo, peso_maximo, color="green", alpha=0.3, label="Faixa de Peso Ideal")

        # Ajustar limites do eixo Y
        peso_min = min(peso_minimo, dados_aluno["Peso"].min()) - 2
        peso_max = max(peso_maximo, dados_aluno["Peso"].max()) + 2
        ax.set_ylim(peso_min, peso_max)

        # Plotar progresso do peso
        ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")
        for x, y in zip(dados_aluno["Data"], dados_aluno["Peso"]):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points", xytext=(0, 10), ha="center")

        ax.set_title("Progresso do Peso")
        ax.set_xlabel("Data")
        ax.set_ylabel("Peso (kg)")
        ax.grid(alpha=0.4, linestyle="--")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        plt.tight_layout()
        st.pyplot(fig)

        # --- Gráfico de Medidas ---
        st.subheader("Progresso das Medidas")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Faixas para cintura
        cintura_max = 94 if sexo == "Masculino" else 80
        cintura_alerta = 102 if sexo == "Masculino" else 88
        ax.axhspan(0, cintura_max, color="green", alpha=0.2, label="Saudável")
        ax.axhspan(cintura_max, cintura_alerta, color="yellow", alpha=0.2, label="Moderado")
        ax.axhspan(cintura_alerta, max(cintura_alerta + 10, dados_aluno["Cintura"].max()), color="red", alpha=0.2, label="Alto Risco")

        # Plotar progresso de cintura e quadril
        ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
        ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")

        ax.set_title("Progresso das Medidas")
        ax.set_xlabel("Data")
        ax.set_ylabel("Medidas (cm)")
        ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))
        plt.tight_layout()
        st.pyplot(fig)

        # --- Feedback ---
        st.subheader("Feedback:")
        imc = dados_aluno["IMC"].iloc[-1]
        st.write(f"**IMC Atual:** {imc}")
except FileNotFoundError:
    st.warning("Sem dados existentes.")

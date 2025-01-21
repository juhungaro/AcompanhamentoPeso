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
altura = st.sidebar.number_input("Altura (em metros)", format="%.2f", min_value=0.0, step=0.01)
peso = st.sidebar.number_input("Peso atual (em kg)", format="%.1f", min_value=0.0, step=0.1)
cintura = st.sidebar.number_input("Circunferência da Cintura (em cm)", format="%.1f", min_value=0.0, step=0.1)
quadril = st.sidebar.number_input("Circunferência do Quadril (em cm)", format="%.1f", min_value=0.0, step=0.1)
data = st.sidebar.date_input("Data da medição", value=dt.date.today())

# Botão para gravar dados
if st.sidebar.button("Salvar Dados"):
    if nome and altura > 0 and peso > 0:
        # Criação ou carregamento da base de dados
        try:
            dados = pd.read_csv("dados_alunos.csv")
        except FileNotFoundError:
            dados = pd.DataFrame(columns=["Nome", "Sexo", "Data", "Altura", "Peso", "Cintura", "Quadril", "IMC", "C/Q"])

        # Cálculos
        imc = round(peso / (altura ** 2), 2) if altura > 0 else None
        razao_cq = round(cintura / quadril, 2) if quadril > 0 else None

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
try:
    dados = pd.read_csv("dados_alunos.csv")

    # Garantir que as colunas estão no formato correto
    dados["Data"] = pd.to_datetime(dados["Data"], errors="coerce")
    dados["Peso"] = pd.to_numeric(dados["Peso"], errors="coerce")
    dados.dropna(subset=["Data", "Peso"], inplace=True)

    # Seleção de aluno para análise
    alunos = dados["Nome"].unique()
    aluno_selecionado = st.selectbox("Selecione um aluno para visualizar os dados", alunos)

    if aluno_selecionado:
        # Filtrar dados do aluno
        dados_aluno = dados[dados["Nome"] == aluno_selecionado].sort_values(by="Data")

        # Exibir tabela de dados
        st.subheader(f"Dados de {aluno_selecionado}")
        st.dataframe(dados_aluno)

        # Verificar se há dados suficientes para plotar
        if len(dados_aluno) > 0:
            # Exibir gráficos de progresso
            st.subheader("Progresso ao longo do tempo")

            # Plotar gráfico de peso com faixa saudável de peso
            fig, ax = plt.subplots(figsize=(12, 6))
            altura_atual = dados_aluno["Altura"].iloc[-1] if not dados_aluno["Altura"].isnull().all() else None

            if altura_atual and altura_atual > 0:
                peso_minimo = round(18.5 * (altura_atual ** 2), 2)
                peso_maximo = round(24.9 * (altura_atual ** 2), 2)

                # Configurar limites do eixo Y incluindo a faixa ideal
                peso_min = min(dados_aluno["Peso"].min() - 2, peso_minimo - 2)
                peso_max = max(dados_aluno["Peso"].max() + 2, peso_maximo + 2)
                ax.set_ylim(peso_min, peso_max)

                # Adicionar faixa de peso saudável
                ax.axhspan(peso_minimo, peso_maximo, color="green", alpha=0.2, label="Faixa de Peso Ideal")

            # Plotar o progresso do peso
            ax.plot(dados_aluno["Data"], dados_aluno["Peso"], marker="o", label="Peso (kg)", color="blue")

            # Adicionar valores nos pontos do gráfico
            for x, y in zip(dados_aluno["Data"], dados_aluno["Peso"]):
                ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')

            # Configurar eixo X para mostrar apenas as datas das pesagens
            ax.set_xticks(dados_aluno["Data"])
            ax.set_xticklabels([d.strftime('%d/%m/%Y') for d in dados_aluno["Data"]], rotation=45)

            ax.set_title("Progresso do Peso com Faixa Ideal")
            ax.set_xlabel("Data")
            ax.set_ylabel("Peso (kg)")
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig)

            # Plotar gráfico de medidas
            fig, ax = plt.subplots(figsize=(12, 6))
            if sexo == "Masculino":
                cintura_max = 94
                cintura_alerta = 102
            else:
                cintura_max = 80
                cintura_alerta = 88

            # Configurar limites do eixo Y
            medida_min = min(dados_aluno["Cintura"].min(), dados_aluno["Quadril"].min()) - 5
            medida_max = max(dados_aluno["Cintura"].max(), dados_aluno["Quadril"].max(), cintura_alerta + 5)
            ax.set_ylim(medida_min, medida_max)

            # Adicionar as faixas de cintura ao gráfico
            ax.axhspan(0, cintura_max, color="green", alpha=0.2, label="Faixa Saudável")
            ax.axhspan(cintura_max, cintura_alerta, color="yellow", alpha=0.2, label="Risco Moderado")
            ax.axhspan(cintura_alerta, medida_max, color="red", alpha=0.2, label="Risco Alto")

            # Plotar o progresso das medidas
            ax.plot(dados_aluno["Data"], dados_aluno["Cintura"], marker="o", label="Cintura (cm)", color="orange")
            ax.plot(dados_aluno["Data"], dados_aluno["Quadril"], marker="o", label="Quadril (cm)", color="purple")

            # Adicionar valores nos pontos do gráfico
            for x, y in zip(dados_aluno["Data"], dados_aluno["Cintura"]):
                ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,10), ha='center')
            for x, y in zip(dados_aluno["Data"], dados_aluno["Quadril"]):
                ax.annotate(f'{y:.1f}', (x, y), textcoords="offset points", xytext=(0,-15), ha='center')

            # Configurar eixo X para mostrar apenas as datas das medições
            ax.set_xticks(dados_aluno["Data"])
            ax.set_xticklabels([d.strftime('%d/%m/%Y') for d in dados_aluno["Data"]], rotation=45)

            ax.set_title("Progresso das Medidas com Faixas Ideais")
            ax.set_xlabel("Data")
            ax.set_ylabel("Medidas (cm)")
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig)

            # Feedback quanto aos parâmetros
            st.subheader("Feedback sobre a saúde")
            imc_atual = dados_aluno["IMC"].iloc[-1]
            
            # Mensagem do IMC
            if imc_atual < 18.5:
                st.warning(f"IMC atual: {imc_atual:.1f} - Classificação: Abaixo do peso")
            elif 18.5 <= imc_atual < 25:
                st.success(f"IMC atual: {imc_atual:.1f} - Classificação: Peso normal")
            elif 25 <= imc_atual < 30:
                st.warning(f"IMC atual: {imc_atual:.1f} - Classificação: Sobrepeso")
            elif 30 <= imc_atual < 35:
                st.error(f"IMC atual: {imc_atual:.1f} - Classificação: Obesidade grau I")
            elif 35 <= imc_atual < 40:
                st.error(f"IMC atual: {imc_atual:.1f} - Classificação: Obesidade grau II")
            else:
                st.error(f"IMC atual: {imc_atual:.1f} - Classificação: Obesidade grau III")
        else:
            st.warning("Não há dados suficientes para exibir os gráficos.")
except FileNotFoundError:
    st.warning("Nenhum dado encontrado. Por favor, insira os dados de um aluno para começar.")

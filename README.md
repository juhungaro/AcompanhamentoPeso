**Monitoramento Físico**

Um aplicativo web para monitoramento de progresso físico de alunos/clientes, desenvolvido com Streamlit.

**🚀 Funcionalidades**
- Inserção de dados físicos de alunos/clientes
- Visualização de progresso individual
- Gráficos interativos para:
  - Progresso do Peso
  - Gordura Visceral
  - Gordura Corporal
  - Massa Muscular
- Remoção de alunos/clientes do sistema

**📋 Pré-requisitos**

- Python 3.7+
- Streamlit
- Pandas
- Matplotlib

**🔧 Instalação**

Clone o repositório:
git clone https://github.com/

Entre no diretório do projeto:
cd monitoramento-fisico

Instale as dependências:
pip install -r requirements.txt

🖥️ Como usar
Execute o aplicativo Streamlit:
streamlit run app.py

Abra o navegador e acesse o endereço local fornecido pelo Streamlit (geralmente http://localhost:8501)
Use o menu lateral para navegar entre as opções:
"Inserir Dados": Adicione novos dados de alunos/clientes
"Visualizar Aluno": Veja o progresso individual e gráficos
📊 Estrutura de Dados
O aplicativo utiliza um arquivo CSV (dados_alunos.csv) para armazenar os dados. A estrutura do CSV é a seguinte:

Nome,Sexo,Data,Altura,Peso,IMC,PercentualGordura,PercentualMassaMagra,GorduraVisceral

🤝 Contribuindo
Contribuições são muito bem-vindas! Siga estes passos:

Faça um fork do projeto
Crie sua feature branch (git checkout -b feature/AmazingFeature)
Commit suas mudanças (git commit -m 'Add some AmazingFeature')
Push para a branch (git push origin feature/AmazingFeature)
Abra um Pull Request
📝 Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE.md para detalhes.

📞 Contato
Seu Nome - @seu_twitter - email@example.com

Link do Projeto: https://github.com/seu-usuario/monitoramento-fisico

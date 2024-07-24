# GitHub and Jira Data Miner Repository

## Sobre o Projeto

GitHub and Jira Data Miner é uma ferramenta projetada para extrair e coletar dados detalhados de projetos no GitHub e no Jira, utilizando as APIs Rest dessas plataformas. Esta ferramenta é ideal para desenvolvedores, pesquisadores e analistas que desejam obter insights profundos sobre a dinâmica dos projetos gerenciados nessas plataformas.

## Funcionalidades

### GitHub

Obtenha informações detalhadas sobre repositórios do GitHub, incluindo:

- **Commits**: Histórico de alterações no repositório.
- **Issues**: Relatórios de problemas ou sugestões de melhorias.
- **Pull Requests**: Propostas de alterações no código.
- **Branches**: Diferentes ramificações de desenvolvimento.

### Jira

Obtenha informações detalhadas sobre os diferentes tipos de issues do Jira, incluindo:

- **Epics**: Grandes corpos de trabalho que podem ser divididos em menores partes, como user stories, tasks, e subtasks.
- **User Stories**: Descrições de funcionalidades do ponto de vista do usuário final. Elas geralmente definem o que o usuário deseja alcançar com o software.
- **Tasks**: Tarefas individuais que precisam ser concluídas. Estas podem ser parte de uma user story ou épico.
- **Subtasks**: Tarefas menores que compõem uma task maior. Subtasks ajudam a dividir tarefas complexas em partes manejáveis.
- **Bugs**: Relatórios de problemas ou erros encontrados no software que precisam ser corrigidos.
- **Enablers**: Itens de trabalho que ajudam a realizar ou suportar a implementação de user stories e épicos. Eles podem incluir atividades como pesquisa, design ou infraestrutura.

## Começando

### Pré-requisitos

Antes de iniciar, certifique-se de que você tem Python 3.8 ou superior instalado em seu sistema. Você também precisará das seguintes bibliotecas Python:

- `requests`: Para realizar chamadas à API do GitHub e Jira.
- `json`: Para manipulação de dados em formato JSON.
- `os`: Para interagir com o sistema operacional.
- `dotenv`: Para carregar variáveis de ambiente do arquivo `.env`.
- `tqdm`: Para mostrar barras de progresso em loops.
- `urlparse`: Para analisar URLs.
- `customtkinter`: Para criar interfaces gráficas de usuário.
- `tkcalendar`: Para criar os campos de seleção de data.
- `tkinter`: Para criar pop-ups.

### Instalação

Siga os passos abaixo para configurar o ambiente e executar a ferramenta:

```bash
# Clone o repositório
git clone https://github.com/aisepucrio/stnl-jiradatamining.git
cd stnl-jiradatamining

# Instale os pré-requisitos
pip install -r requirements.txt

# Entre na pasta source do projeto
cd ./src

# Inicie o framework
python main.py
```

### Configuração

1. Após iniciar, o menu de seleção de plataformas do framework será exibido.
2. Antes de selecionar qualquer plataforma, você precisa configurar suas credenciais.
3. Para fazer isso, selecione o ícone de configurações no canto inferior esquerdo da interface.
4. Ao clicar, abrirá uma janela para você inserir seus dados (Tokens, usuários e emails).
5. Após inserir e clicar em "Add", você pode fechar a janela e selecionar a plataforma que deseja utilizar no framework.

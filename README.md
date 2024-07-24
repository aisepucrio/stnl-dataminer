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

Antes de iniciar, certifique-se de que você tem Python 3.11 ou superior instalado em seu sistema.

### Instalação

Siga os passos abaixo para configurar o ambiente e executar a ferramenta:

```bash
# Clone o repositório
git clone https://github.com/aisepucrio/stnl-dataminer.git
cd stnl-dataminer

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
3. Para fazer isso, selecione o ícone de configurações no canto inferior direito da interface.
4. Ao clicar, abrirá uma janela para você inserir seus dados de acordo com a imagem: GitHub Tokens e GitHub Users se referem às suas credenciais do GitHub; API Email e API Token se referem às suas credenciais do Jira; Save Path é o local onde o arquivo de mineração será salvo; e Number of Max Workers é o número de threads que seu computador irá usar.
5. Após inserir e clicar em "Add", você pode fechar a janela e selecionar a plataforma que deseja utilizar no framework.


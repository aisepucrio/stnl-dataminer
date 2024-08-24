
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

# Inicie o framework
python main.py
```

### Configuração

1. Após iniciar, o menu de seleção de plataformas do framework será exibido.
2. Antes de selecionar qualquer plataforma, você precisa configurar suas credenciais.
3. Para fazer isso, selecione o ícone de configurações no canto inferior direito da interface.
4. Ao clicar, abrirá uma janela para você inserir seus dados de acordo com a imagem:

- **GitHub Tokens:** Seus tokens do GitHub.
- **GitHub Users:** Seus usuários do GitHub.
- **API Email:** Suas credenciais do Jira.
- **API Token:** Seus token da API do Jira.
- **Save Path:** O local onde o arquivo de mineração será salvo.
- **Number of Max Workers:** O número de threads que seu computador irá usar.

5. Após inserir e clicar em "Add", você pode fechar a janela e selecionar a plataforma que deseja utilizar no framework.

**Observação:** Para o funcionamento ideal do framework, é recomendado que tenha pelo menos 2 tokens.

### Passo Opcional: Instalação do Tkinter

Em algumas distribuições Linux e no macOS, o Tkinter pode precisar ser instalado separadamente, usando o sistema de pacotes do sistema e não pelo `pip`. Para instalar o Tkinter, siga os comandos específicos da sua distribuição:

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get install python3-tk
  ```

- **Fedora:**
  ```bash
  sudo dnf install python3-tkinter
  ```

- **macOS (via Homebrew):**
  ```bash
  brew install python-tk
  ```

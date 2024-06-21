# MeetMaster - Sistema de Gestão de Eventos

### Requisitos Locais

- Docker
- (Opcional) VSCode e Dev Containers (ms-vscode-remote.remote-containers)

## Configuração do Ambiente de Desenvolvimento

<details>
<summary><strong>Configurando o Container de Desenvolvimento com VSCode</strong></summary>

Siga estes passos para configurar um container de desenvolvimento com todas as ferramentas e dependências necessárias para o projeto.

1. Construa as variáveis de ambiente do container de desenvolvimento:
    ```sh
    bash ./.devcontainer/scripts/setup_build_env_vars.sh
    ```

2. Abra o projeto no VSCode.

3. Use o palette de comandos (Ctrl+Shift+P) e selecione:
    ```
    Dev Container: Open Folder in Container
    ```

4. Aguarde a construção do container. Após a conclusão, configure/entre no ambiente virtual:
    ```sh
    venv
    ```

</details>

<details>
<summary><strong>Executando o Container de Desenvolvimento sem o VSCode Dev Containers</strong></summary>

Se você preferir não usar o VSCode Dev Containers, você pode executar o container de desenvolvimento diretamente usando o Docker:

1. Navegue até o diretório `.devcontainer` e configure as variáveis de ambiente:
    ```sh
    cd .devcontainer && bash ./scripts/setup_build_env_vars.sh
    ```

2. Execute o container de desenvolvimento:
    ```sh
    docker compose -f docker-compose-dev.yml run dev zsh
    ```

3. Quando o container estiver em execução, ative o ambiente virtual:
    ```sh
    venv
    ```

4. Execute os testes com:
    ```sh
    pytest meetmaster -n auto
    ```

5. Ou execute o servidor com:
    ```sh
    python meetmaster/manage.py runserver [PORT - opcional]
    ```

</details>

## Executando o Container de Produção

Para executar o container de produção, execute os seguintes comandos:

1. Derrube qualquer container existente:
    ```sh
    docker compose down
    ```

2. Construa o container de produção:
    ```sh
    docker compose build
    ```

3. Inicie o container de produção:
    ```sh
    docker compose up
    ```

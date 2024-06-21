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

</details>

<details>
<summary><strong>Executando os Testes</strong></summary>

Após ativar o ambiente virtual:

```sh
pytest meetmaster -n auto
```

</details>

<details>
<summary><strong>Executando o Servidor</strong></summary>

Após ativar o ambiente virtual:

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

## Rotas

As rotas principais do sistema estão configuradas da seguinte maneira:

- `/admin/`: Rota para a interface de administração do Django.
- `/api/`: Rota base para as APIs do sistema, incluindo:
  - `/api/users/`: Endpoints para gerenciamento de usuários.
  - `/api/events/`: Endpoints para gerenciamento de eventos.
- `/api-auth/`: Rota para autenticação da API utilizando o Django REST Framework.

<details>
<summary><strong>Endpoints de Usuários</strong></summary>

- **GET /api/users/**: Lista todos os usuários. (Permissão: Superuser)
- **POST /api/users/**: Cria um novo usuário. (Permissão: Pública)
- **GET /api/users/{id}/**: Recupera os detalhes de um usuário específico. (Permissão: Autenticado)
- **PUT /api/users/{id}/**: Atualiza um usuário específico. (Permissão: Superuser ou o próprio usuário)
- **DELETE /api/users/{id}/**: Deleta um usuário específico. (Permissão: Superuser ou o próprio usuário)
- **POST /api/users/{id}/change_password/**: Altera a senha de um usuário específico. (Permissão: Superuser ou o próprio usuário)

</details>

<details>
<summary><strong>Endpoints de Eventos</strong></summary>

- **GET /api/events/**: Lista todos os eventos. (Permissão: Autenticado ou leitura pública)
- **POST /api/events/**: Cria um novo evento. (Permissão: Autenticado)
- **GET /api/events/{id}/**: Busca os detalhes de um evento específico. (Permissão: Autenticado ou leitura pública)
- **PUT /api/events/{id}/**: Atualiza um evento específico. (Permissão: Dono do evento)
- **DELETE /api/events/{id}/**: Deleta um evento específico. (Permissão: Dono do evento)
- **POST /api/events/{id}/cancel/**: Cancela um evento específico. (Permissão: Dono do evento)
- **GET /api/events/{id}/attendees/**: Lista os participantes de um evento específico. (Permissão: Dono do evento ou participante)
- **POST /api/events/{id}/attende/**: Adiciona o usuário autenticado como participante do evento. (Permissão: Autenticado)
- **POST /api/events/{id}/remove_attendee/**: Remove o usuário autenticado como participante do evento. (Permissão: Autenticado)

</details>

Notificações:
- **Atualizar evento**: Todos usuários participantes são notificados por email
- **Cancelar evento**: Todos usuários participantes são notificados por email
- **Adicionar a si como participante**: Usuário é notificado por email
- **Remover a si como participante**: Usuário é notificado por email

</details>

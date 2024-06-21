# MeetMaster - Event Management System

## Development Environment Setup

### Local Requirements

- Docker
- (Optional) VSCode and Dev Containers (ms-vscode-remote.remote-containers)

<details>
<summary><strong>Setting Up Development Container with VSCode</strong></summary>

Follow these steps to set up a development container with all the necessary tools and dependencies for the project.

1. Build dev container environment variables:
    ```sh
    bash ./.devcontainer/scripts/setup_build_env_vars.sh
    ```

2. Open the project in VSCode.

3. Use the command palette (Ctrl+Shift+P) and select:
    ```
    Dev Container: Open Folder in Container
    ```

4. Wait for the container to build. Once the build is complete, set up/enter the virtual environment:
    ```sh
    venv
    ```

</details>

<details>
<summary><strong>Running the Developer Container without VSCode Dev Containers</strong></summary>

If you prefer not to use VSCode Dev Containers, you can run the developer container using Docker directly:

1. Navigate to the `.devcontainer` directory and set up environment variables:
    ```sh
    cd .devcontainer && bash ./scripts/setup_build_env_vars.sh
    ```

2. Run the developer container:
    ```sh
    docker compose -f docker-compose-dev.yml run dev zsh
    ```

3. When the container is running, activate the virtual environment:
    ```sh
    venv
    ```

4. Run the tests with:
    ```sh
    pytest meetmaster -n auto
    ```

5. Or run the server with:
    ```sh
    python meetmaster/manage.py runserver [PORT - optional]
    ```

</details>

<details>
<summary><strong>Running the Production Container</strong></summary>

To run the production container, execute the following commands:

1. Bring down any existing containers:
    ```sh
    docker compose down
    ```

2. Build the production container:
    ```sh
    docker compose build
    ```

3. Start the production container:
    ```sh
    docker compose up
    ```

</details>

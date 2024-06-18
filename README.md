# MeetMaster - Event Management System  ---- DRAFT

---

## Devolopment Environment Setup

### Local Requirements

- Docker
- (Optional) VSCode and Dev Containers (ms-vscode-remote.remote-containers)

You can omit the following requirements if you are using VSCode with Dev Containers.

- Python 3.10


### Development container with VSCode .devcontainer

Running the following commands will setup a development container with all the necessary tools and dependencies for the project.

- Build dev container environment variables
```sh
bash ./.devcontainer/scripts/setup_build_env_vars.sh
``` 

- Open the project in VSCode

- Ctrl+Shift+P -> Dev Container: Open Folder in Container

Wait for the container to build and when it's done run the following to setup/enter the virtual environment.

```sh
venv
```

---

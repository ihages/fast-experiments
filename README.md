# Learning: FastAPI Tutorial

This experiment follows the steps at https://fastapi.tiangolo.com/tutorial.

## First Steps

### Initializing Project Environment and Repository

- created github repo
- created venv with `python -m venv .venv`
- installed fastapi with `python -m pip install "fastapi[standard]"`

### Running project

With venv activated, in the project root, run `fastapi dev`. This will run the server.

Default configuration does not handle authorization. This will be covered later.

APIs can be fetched via curl commands or using a web browser. Default port is `localhost:8000`.

While fastapi dev is running, call logs will show in terminal.

Fast also has a Swagger UI library to view your endpoints. This can be found at `localhost:8080/docs`.

> Question: How can we host this server externally? Can it be hosted on Github? On Azure? On AWS?

### Configuring Entry Point

This allows where the FastAPI app is located in a project, in case it is not at root/main.py. In root/pyproject.toml,

```toml
[tool.fastapi]
entrypoint = "main:app"
```

This coorelates to `from main import app`. Folder notation for this would be `folder.main:app`, where path is `root/folder/main.py`

### Deployment with FastAPI Cloud

Deploy using `fastapi deploy`. If you aren't logged in, it will have an interractive CLI screen to log you in. This account can be made with GitHub (easy peasy).

The CLI will then create an app for you and attempt to build and deploy. This failed my first time.

**Why it failed:**

Needed build system and project metadata, where the requirements would be established.

```[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "fast-experiments"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi[standard]",
]
```

After fixing this, deployment was made ready at https://fast-experiments.fastapicloud.dev

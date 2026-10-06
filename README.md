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

## Path Parameters

These are defined by

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}
```

In testing with localhost, request `localhost:8000/items/item%20` returns `{"item_id":"item 1"}`. Remember `%20` is `space`.

## Parameter Typing

The inputs can also have types declared within the function parameters. Passing through a parameter of an invalid type will return a [422 error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422):

```
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": [
        "path",
        "item_id"
      ],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "item 1"
    }
  ]
}
```

Establishing a type will also make sure the endpoint reads the parameter as an int, rather than a string. For example, `/items/3` will know that 3 is the `3`, not `"3"`. The json will thus be `{"item_id":3}`.

These path parameters can be interractive via the Swagger UI page, as well.

## Similar Paths and Declaration Order

You can use the same path for multiple endpoints, just as long as the declaration order makes sense. This would be suitable in the case of potential `users` endpoints like this:

```
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

The fixed `/me` endpoint must come before the dynamic, or else the "me" would be processed as an input parameter rather than a fixed route.

You cannot have duplicate routes with the same exact path. The first one would always be used.

## Predefined Parameter Input Options

You can set a defined list of options for a parameter input by creating an Enum in python.

```
class Options(str, Enum):
  apple="apple"
  banana="banana"
  carrot="carrot"

@app.get("/opt/{option}")
async def get_option(option:Options):
  match (option):
    case Options.apple:
      return {"option":option,"message":"An apple a day keeps the doctor away."}
    case Options.banana:
      return {"option":option,"message":"This is so bananas, b-a-n-a-n-a-s!"}
    case Options.carrot:
          return {"option":option,"message":"You chose a vegetable. Quite the contrarian, you are."}
```

In Swagger, the input will become a dropdown selection.

If you violate the type defintion via curl request or browser request, you will get a 422 error. Luckily, this error will remind you of your options.

```
{
  "detail": [
    {
      "type": "enum",
      "loc": [
        "path",
        "option"
      ],
      "msg": "Input should be 'apple', 'banana' or 'carrot'",
      "input": "pear",
      "ctx": {
        "expected": "'apple', 'banana' or 'carrot'"
      }
    }
  ]
}
```

## Paths as Parameters

Due to the parameter syntax reserving `/`, paths as inputs cannot be passed through to a parameter normally... in OpenAPI (the basis for FastAPI).

FastAPI fixed this issue. The internal tool Starlett allows `@app.get("/files/{file_path:path}")`, which would allow any path including `/` to count as one parameter. This must be the last parameter in a path, if used.

Given

```
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```

calling `http://localhost:8000/files/home/johndoe/myfile.txt` would return `{"file_path":"home/johndoe/myfile.txt"}`

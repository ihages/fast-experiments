# Learning: FastAPI Tutorial

This experiment follows the steps at https://fastapi.tiangolo.com/tutorial.

## First Steps

https://fastapi.tiangolo.com/tutorial/first-steps/

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

https://fastapi.tiangolo.com/tutorial/path-params/

These are defined by

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
  return {"item_id": item_id}
```

In testing with localhost, request `localhost:8000/items/item%20` returns `{"item_id":"item 1"}`. Remember `%20` is `space`.

### Parameter Typing

The inputs can also have types declared within the function parameters. Passing through a parameter of an invalid type will return a [422 error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/422):

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "item_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "item 1"
    }
  ]
}
```

Establishing a type will also make sure the endpoint reads the parameter as an int, rather than a string. For example, `/items/3` will know that 3 is the `3`, not `"3"`. The json will thus be `{"item_id":3}`.

These path parameters can be interractive via the Swagger UI page, as well.

### Similar Paths and Declaration Order

You can use the same path for multiple endpoints, just as long as the declaration order makes sense. This would be suitable in the case of potential `users` endpoints like this:

```python
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

### Predefined Parameter Input Options

You can set a defined list of options for a parameter input by creating an Enum in python.

```python
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

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": ["path", "option"],
      "msg": "Input should be 'apple', 'banana' or 'carrot'",
      "input": "pear",
      "ctx": {
        "expected": "'apple', 'banana' or 'carrot'"
      }
    }
  ]
}
```

### Paths as Parameter Inputs

Due to the parameter syntax reserving `/`, paths as inputs cannot be passed through to a parameter normally... in OpenAPI (the basis for FastAPI).

FastAPI fixed this issue. The internal tool Starlett allows `@app.get("/files/{file_path:path}")`, which would allow any path including `/` to count as one parameter. This must be the last parameter in a path, if used.

Given

```python
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
  return {"file_path": file_path}
```

calling `http://localhost:8000/files/home/johndoe/myfile.txt` would return `{"file_path":"home/johndoe/myfile.txt"}`

### Validations

You can set validation rules for them when they are provided (optional or not). This requires `Path` from `fastapi` and `Annotated` from `typing`. This works the same for queries, which has example implementations [below](#query-parameters-validation)

- max_length -- maximum amount of characters
- min_length -- minimum amount of characters
- default -- default value
- pattern -- regex match
- title -- meta title for field
- description -- meta description for field
- alias -- variable as it's called in FastAPI (if name isn't python legal)
- depreciated -- meta label for depreciated (boolean, default False)
- include_in_schema -- show in OpenAPI schema (boolean, default True)
- gt -- greater than
- lt -- less than
- et -- equal to
- ge -- greater than or equal to
- le -- less than or equal to

## Query Parameters

https://fastapi.tiangolo.com/tutorial/query-params/

### What's the difference?

Path parameters determine the identity of the data. Query parameters should change how the data is represented. Query parameters are usually used for pagination, filtering, sorting, and searching. Query parameters are optional, as well.

### Defining Query Parameters

To declare query parameters, the parameters go in the endpoint function, but not the path.

```python
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
  return fake_items_db[skip : skip + limit]
```

These query parameters will show up as inputs in the Swagger UI.

### Boolean Parameter Conversions

FastAPI handles Boolean naming conversions. So `1`, `True`, `true`, `on`, and `yes` (all case insensitive) are all functionally identical.

### Validation {#query-parameters-validation}

You can set validation rules for them when they are provided (optional or not). This requires `Query` from `fastapi` and `Annotated` from `typing`. For this example, we have a parameter `q: str | None`, that we want to ensure the string never exceeds 50 characters. This is done by doing the following:

```python
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10, search: Annotated[ str | None, Query(max_length=50)] = None):
  filtered_items = []
  if not search: filtered_items = fake_items_db
  else:
    for i in fake_items_db:
      if search.lower() in i["item_name"].lower():
        filtered_items.append(i)
  return filtered_items[skip : skip + limit]
```

If the input exceeds the limit, it will respond with a 422 error:

```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["query", "search"],
      "msg": "String should have at most 50 characters",
      "input": "b123456789012345678901234567890123456789012345678901234567890",
      "ctx": {
        "max_length": 50
      }
    }
  ]
}
```

The `Annotated` type is primarily used to add metadata to the function. Adding `Query` tells FastAPI the validation to have on said value. `Query` is for "Query Parameter", not like the Query used for SQL. Query includes the validations

- max_length -- maximum amount of characters
- min_length -- minimum amount of characters
- default -- default value
- pattern -- regex match
- title -- meta title for field
- description -- meta description for field
- alias -- variable as it's called in FastAPI (if name isn't python legal)
- depreciated -- meta label for depreciated (boolean, default False)
- include_in_schema -- show in OpenAPI schema (boolean, default True)
- gt -- greater than
- lt -- less than
- et -- equal to
- ge -- greater than or equal to
- le -- less than or equal to

Query parameters can also pass lists of items by using `item: Annotated[list[str], Query()]` and passing it through the request path as `localhost:8000/items/?item=foo&item=bar`. Defaults are defined using array notation.

`Annotated` also allows for custom validation functions, using the `pydantic` function `AfterValidator`. This works like

```python
def check_valid_id(id: str):
  if not id.startswith(("isbn-", "imdb-")):
    raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
  return id


@app.get("/items/")
async def read_items(
  id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
  if id:
    item = data.get(id)
  else:
    id, item = random.choice(list(data.items()))
  return {"id": id, "name": item}
```

You can also create Query Parameter Models using the pydantic `BaseModel` and `Field`. This allows you to use that model for multiple different endpoints without having to redefine it. Example:

```python
class FilterParams(BaseModel):
  limit: int = Field(100, gt=0, le=100)
  offset: int = Field(0, ge=0)
  order_by: Literal["created_at", "updated_at"] = "created_at"
  tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
  return filter_query
```

You can also strictly forbid insertion of additional query parameters via the commandline. If the model had `model_config = {"extra": "forbid"}` in it, then passing through a request `https://example.com/items/?limit=10&tool=plumbus` would return an Error, as tool was not a defined parameter in the model:

```json
{
  "detail": [
    {
      "type": "extra_forbidden",
      "loc": ["query", "tool"],
      "msg": "Extra inputs are not permitted",
      "input": "plumbus"
    }
  ]
}
```

## Request Body

https://fastapi.tiangolo.com/tutorial/body/

The request body allows sending large data as json to the server. This is helpful in cases like uploading data, investigating geojson geometry, or parsing context.

Sending data is not wholey compatable with GET requests. It is most functional with POST, PUT, DELETE, or PATCH.

Using request bodies requires a defined data structure. This can be done using `BaseModel` from the data validation library pydantic:

```python
class Item(BaseModel):
  name:str
  description: str | None = None
  price: float
  tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
  return item
```

This would have a JSON request body such as:

```json
{
  "name": "Foo",
  "description": "An optional description",
  "price": 45.2,
  "tax": 3.5
}
```

Since the configuration of the Item type is a pydantic `BaseModel`, not included in the path parameters, FastAPI will automatically know to expect a request body. FastAPI will also validate the data per entry and convert types if needed. A fun extension of FastAPI is that it creates JSON schemas for requests and responses. This can be used by [Orval](https://orval.dev/docs/) to generate TypeScript types in React frontends. This schema is also visible in Swagger.

Due to the type recognition of all parameter types, you can use path, query, and request body parameters in tandem.

You can also have multiple body request parameters, as long as they each have their own `BaseModel` class. Where `Item` and `User` both extend `BaseModel`,

```python
async def update_item(item_id: int, item: Item, user: User):
```

expects the request body:

```json
{
  "item": {
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2
  },
  "user": {
    "username": "dave",
    "full_name": "Dave Grohl"
  }
}
```

If it was only one body request variable, the wrappers `"item"` and `"user"` would not be needed. But with both, they must be separated by variable.

When creating a body parameter, you can specify it as such as defining the variable as `item: Annotated[Item, Body(embed=True)]`. This will force the json to render the variable wrappers, even if there's only one of them.

**with embed:** `{"item": {"name": "Foo", "description": "The pretender", "price": 42.0, "tax": 3.2}}`

**without embed:** `{"name": "Foo", "description": "The pretender", "price": 42.0, "tax": 3.2}` |

`pydantic`'s `Field` can be used like `FastAPI`'s `Body`, `Query`, and `Path`, but this time, within the `BaseModel` class.

These models can also be nested within each other. This is getting into TypeScript territory here (yay!)

```python
class Image(BaseModel):
  url: str
  name: str


class Item(BaseModel):
  name: str
  description: str | None = None
  price: float
  tax: float | None = None
  tags: set[str] = set()
  image: Image | None = None
```

You can also declare example data in a `BaseModel`'s `model_config` variable:

```python
class Item(BaseModel):
  name: str
  description: str | None = None
  price: float
  tax: float | None = None

  model_config = {
    "json_schema_extra": {
      "examples": [
        {
          "name": "Foo",
          "description": "A very nice Item",
          "price": 35.4,
          "tax": 3.2,
        }
      ]
    }
  }
```

`Field` function also has prop `examples`, which is a any-type list that can hold example inputs:

```python
class Item(BaseModel):
  name: str = Field(examples=["Foo"])
  description: str | None = Field(default=None, examples=["A very nice Item"])
  price: float = Field(examples=[35.4])
  tax: float | None = Field(default=None, examples=[3.2])
```

`examples` can also be used in any of the FastAPI parameter functions. These examples will show in the Swagger UI.

## Additional Data Types

https://fastapi.tiangolo.com/tutorial/extra-data-types/

- UUID -- unique universal id
- datetime.datetime -- python datetime in ISO 8601 format
- datetime.date -- python datetime in ISO 8601
- dateime.timedelta -- python time change in total seconds as float
- frozenset -- set with unique entries. Converted to set in requests and list in responses.
- bytes -- binary as string
- decimal -- handled the same as floats

These must be imported.

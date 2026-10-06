from enum import Enum
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()

@app.get("/")
def get_root():
  return {"Hello":"World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
  return {"item_id": item_id}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10, search: Annotated[ str | None, Query(max_length=50)] = None):
  filtered_items = []
  if not search: filtered_items = fake_items_db
  else: 
    for i in fake_items_db:
      if search.lower() in i["item_name"].lower():
        filtered_items.append(i)
  return filtered_items[skip : skip + limit]

class Item(BaseModel):
  name:str
  description: str | None = None
  price: float
  tax: float | None = None
  
@app.post("/items/")
async def create_item(item: Item):
  return item
  
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

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
  return {"file_path": file_path}
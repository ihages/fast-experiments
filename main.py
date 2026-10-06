from enum import Enum
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_root():
  return {"Hello":"World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
  return {"item_id": item_id}

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
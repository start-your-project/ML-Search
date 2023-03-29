from pydantic import BaseModel
from fastapi import FastAPI
from .searchplay import get_search_engine
#from .search_engine import SearchEngine
from src.data import read_data_paths_params

class Query(BaseModel):
    query: str

app = FastAPI()
SEARCH_ENGINE = None
CONFIG_PATH = "configs/search_config.yaml"

@app.on_event("startup")
def load_search_engine():
    global SEARCH_ENGINE, CONFIG_PATH
    data_paths = read_data_paths_params(CONFIG_PATH)
    SEARCH_ENGINE = get_search_engine(data_paths)


@app.get("/")
async def root():
    return "Search service by @FedorX8"


@app.get("/search/{query}")
async def root(query: str):
    profession = SEARCH_ENGINE.search(query)
    return {"profession": profession}




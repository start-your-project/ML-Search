import os
from pydantic import BaseModel
from fastapi import FastAPI
from typing import Any

from .search_runtime.searchplay import get_search_engine
from src.data import read_data_paths_params
from .search_runtime.search_engine import SearchEngine

from .cv_analyze.cv_process import Recommend, CV, get_recommendation_cv

class Query(BaseModel):
    query: str

app = FastAPI()
SEARCH_ENGINE : SearchEngine

@app.on_event("startup")
def load_search_engine():
    global SEARCH_ENGINE
    config_path = os.getenv("SEARCH_CONFIG_PATH")
    data_paths = read_data_paths_params(config_path)
    SEARCH_ENGINE = get_search_engine(data_paths)


@app.get("/")
async def root():
    return "Search service by @FedorX8"


@app.get("/search/{query}")
async def search(query: str):
    profession = SEARCH_ENGINE.search(query)
    return {"profession": profession}

@app.get("/recommend/{query}")
async def recommend(query: str, n: int = 5):
    professions = SEARCH_ENGINE.recommend(query, n)
    return {"professions": professions}


@app.post("/cv_analyze")
async def get_data(cv: CV) -> Recommend:
    # Waits for the request and converts into JSON
    raw_text = cv.cv_text
    rec = get_recommendation_cv(raw_text, cv.n_tech)
    return Recommend(recommend=rec)




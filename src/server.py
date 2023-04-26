import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from .search_runtime.searchplay import get_search_engine, check_possible_prof
from .search_runtime.search_engine import SearchEngine
from .cv_analyze.recommend_cv_role import Recommend, CV, get_recommend
from .cv_analyze.load_data import load_synonyms, load_freq
from .backward_search.recommend import get_recommend_tech
from src.data import read_data_paths_params


class Query(BaseModel):
    query: str


app = FastAPI()
SEARCH_ENGINE: SearchEngine
CONNECTION_POOL: SimpleConnectionPool
TECH_SYN = {}  # bad_name -> good name
ROLE_TECH_FREQ = {}
API_PREFIX = "/api/v3"
THRESHOLD = 0.08


@app.on_event("startup")
def load_search_engine():
    global SEARCH_ENGINE
    config_path = os.getenv("SEARCH_CONFIG_PATH")
    data_paths = read_data_paths_params(config_path)
    SEARCH_ENGINE = get_search_engine(data_paths, THRESHOLD)
    print("SEARCH ENGINE is initialized")


@app.on_event("startup")
def get_connection_pool():
    global CONNECTION_POOL
    CONNECTION_POOL = psycopg2.pool.SimpleConnectionPool(1, 10,
                                                         user="docker",
                                                         password="docker",
                                                         host="51.250.86.4",
                                                         port="5432")
    if CONNECTION_POOL:
        print("CONNECTION POOL is initialized")
    else:
        print("CONNECTION POOL initialization ERROR")


@app.on_event("startup")
def load_syn():
    global TECH_SYN, ROLE_TECH_FREQ
    TECH_SYN = load_synonyms(CONNECTION_POOL)
    ROLE_TECH_FREQ = load_freq(CONNECTION_POOL, TECH_SYN)


@app.get("/")
async def root():
    return "Search service by @FedorX8"


@app.get(API_PREFIX+"/role_search/{query}")
async def search(query: str) -> dict[str, str]:
    profession = SEARCH_ENGINE.search(query)
    if not profession:
        if check_possible_prof(query):
            return {"profession": query, "in_base": 0}
        raise HTTPException(status_code=404, detail="Nothing was found")
    return {"profession": profession, "in_base": 1}


@app.get(API_PREFIX+"/tech_search/{query}")
async def backward_search(query: str, n:int = 5) -> dict[str, list[str]]:
    result = get_recommend_tech(query, n, CONNECTION_POOL)
    return {"techs": result}


@app.get(API_PREFIX+"/recommend/{query}")
async def recommend(query: str, n: int = 5) -> dict[str, list[str]]:
    professions = SEARCH_ENGINE.recommend(query, n)
    if not professions:
        raise HTTPException(status_code=404, detail="Nothing was found")
    return {"professions": professions}


@app.post(API_PREFIX+"/cv_analyze")
async def get_cv_recommendation(cv: CV) -> Recommend:
    #result = get_recommend_cv(cv.cv_text, cv.role, cv.n_tech, CONNECTION_POOL)
    result = get_recommend(cv.cv_text, cv.role, cv.n_tech, TECH_SYN, ROLE_TECH_FREQ)
    if result.empty():
        raise HTTPException(status_code=404, detail="No such role")
    return result

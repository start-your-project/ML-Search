from pydantic import BaseModel
import psycopg2
from dataclasses import dataclass
import re
from collections import defaultdict

class CV(BaseModel):
    cv_text: str
    n_tech: int = 10
    n_prof: int = 7

class Recommend(BaseModel):
    recommend: list[dict]

def get_clean_text(text: str) -> str:
    pattern = re.compile(r'\s+')
    text = re.sub(pattern, ' ', text).lower()
    text = re.sub("[0-9]", "", text)
    text = re.sub("[^A-Za-z+#]", " ", text)
    text = re.sub("\s+", " ", text).strip()
    return text

def get_recommend_cv(input_cv: str, )


from psycopg2.pool import SimpleConnectionPool
from pydantic import BaseModel
from dataclasses import dataclass
import re


class CV(BaseModel):
    cv_text: str
    role: str
    n_tech: int = 10


class Recommend(BaseModel):
    recommend: list[dict[str, list]]

    def empty(self) -> bool:
        sum_n = 0
        for key in self.recommend[0]:
            sum_n += len(self.recommend[0][key])
        return sum_n == 0

@dataclass
class Row():
    id_technology: int
    name_technology: str
    id_position: int
    name_position: str
    distance: float
    professionalism: float


def has_rus(text: str) -> bool:
    txt = re.findall('[А-яёЁ]+', text)
    if txt:
        return True
    return False


def get_clean_text(text: str) -> str:
    text = re.sub("[^0-9A-Za-zа-яА-ЯЁё\+# ]", " ", text)
    text = re.sub("\s+", " ", text).strip().lower()
    return text


def get_learned(cv_words: list[str], techs: list[tuple[str, float]], n: int = 5) -> list[str]:
    result = []
    for tech, freq in techs:
        tech_words = get_clean_text(tech).split()
        if len(tech_words) == 1:
            if get_clean_text(tech) in cv_words:
                result.append((tech, freq))
        else:
            for tech_w in tech_words:
                if tech_w not in cv_words:
                    break
            else:
                result.append((tech, freq))
    result = sorted(result, key=lambda x: x[1], reverse=True)
    techs = list(map(lambda x: x[0], result))
    n = min(n, len(techs))
    return techs[:n]

def get_to_learn(cv_words: list[str], techs: list[tuple[str, float]], n: int = 5) -> list[str]:
    result = []
    for tech, freq in techs:
        tech_words = get_clean_text(tech).split()
        if len(tech_words) == 1:
            if get_clean_text(tech) not in cv_words:
                result.append((tech, freq))
        else:
            for tech_w in tech_words:
                if tech_w in cv_words:
                    break
            else:
                result.append((tech, freq))

    result = sorted(result, key=lambda x: x[1], reverse=True)
    techs = list(map(lambda x: x[0], result))
    n = min(n, len(techs))
    return techs[:n]


def get_recommend_cv(input_cv: str, role: str, n: int, postgres_pool: SimpleConnectionPool) -> Recommend:
    cv_words = get_clean_text(input_cv).split()
    techs_freq = []
    known_techs = []
    to_know_techs = []

    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM technology_position')
        for elem in cursor:
            row = Row(*elem)
            if not has_rus(row.name_technology) and row.name_position == role:
                techs_freq.append((row.name_technology, row.distance))
        if techs_freq:
            print(f"techs freq: {techs_freq}")
            known_techs = get_learned(cv_words, techs_freq, n)
            to_know_techs = get_to_learn(cv_words, techs_freq, n)

        cursor.close()
        postgres_pool.putconn(connection)
        print("PostgreSQL connection is returned to the pool")
    else:
        print("Error creation connection")
    return Recommend(recommend=[{
        "learned": known_techs,
        "to learn": to_know_techs
    }])

'''
{
  "cv_text": "machine learning engineer ++ developer + github com superaiyah fedorx safonovfedya gmail com codeforces fedorx moscow russia gpa c++ image meda center gui wxwidgets astra linux cmake vk ml ml c c++ dl school cnn alexnet vgg resnet densenet inseption segnet u net rcnn vae cvae java java git + gif code review tinkoff b online alias c++ alias online uml qt youtube best data science + c++ ii ii python numpy pandas matplotlib seaborn pytorch catboost scikit learn aiogram unittest ++ gtest cmake qt wxwidgets java linux sql ms sql mysql git ci cd team work",
  "role": "ML Researcher",
  "n_tech": 10
}
'''





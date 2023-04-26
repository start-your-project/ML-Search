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
    text = re.sub("[^0-9A-Za-zа-яА-ЯЁё\d\+# ]", " ", text)
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


def get_recommend(input_cv: str,
                  role: str,
                  n: int,
                  syn: dict[str, str],
                  role_tech_dist: dict) -> Recommend:
    cv_text = get_clean_text(input_cv)
    cv_words = cv_text.split()

    if role not in role_tech_dist:
        return Recommend(recommend=[{
        "learned": [],
        "to_learn": []
    }])

    all_techs = syn.keys()
    role_techs = role_tech_dist[role]
    learned = set()
    to_learn = set()

    for tech in all_techs:
        tech_cleaned = get_clean_text(tech)
        true_name = syn[tech]

        if has_rus(true_name) or true_name not in role_techs:
            continue

        if len(tech_cleaned.split()) > 1:
            if tech_cleaned in cv_text:
                learned.add(true_name)
            else:
                to_learn.add(true_name)
        else:
            if tech_cleaned in cv_words:
                learned.add(true_name)
            else:
                to_learn.add(true_name)

    print("LEARNED")
    print(learned)
    print("TO_LEARN")
    print(to_learn)
    to_learn = to_learn - learned

    learned_dist = [(tech, role_tech_dist[role][tech]) for tech in learned]
    to_learn_dist = [(tech, role_tech_dist[role][tech]) for tech in to_learn]

    learned_dist = sorted(learned_dist, key=lambda p: -p[1])
    to_learn_dist = sorted(to_learn_dist, key=lambda p: -p[1])

    learned_ans = list(map(lambda x: x[0], learned_dist[:min(n, len(learned_dist))]))
    to_learn_ans = list(map(lambda x: x[0], to_learn_dist[:min(n, len(to_learn_dist))]))

    return Recommend(recommend=[{
        "learned": learned_ans,
        "to_learn": to_learn_ans
    }])



def get_recommend_cv(input_cv: str, role: str, n: int, syn: dict[str, str]) -> Recommend:
    cv_text = get_clean_text(input_cv)
    cv_words = cv_text.split()
    techs_freq = []
    known_techs = []
    to_know_techs = []

    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT name_technology, name_position, distance FROM technology_position')
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

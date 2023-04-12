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

@dataclass
class Row():
    id_technology: int
    name_technology: str
    id_position: int
    name_position: str
    distance: float
    professionalism: float

def get_clean_text(text: str) -> str:
    pattern = re.compile(r'\s+')
    text = re.sub(pattern, ' ', text).lower()
    text = re.sub("[0-9]", "", text)
    text = re.sub("[^A-Za-z+#]", " ", text)
    text = re.sub("\s+", " ", text).strip()
    return text

def has_rus(text: str) -> bool:
    txt = re.findall('[А-яёЁ]+', text)
    if txt:
        return True
    return False

def get_abbr(text: str) -> str:
    result = ""
    if len(text.split()) == 1:
        return text
    for word in text.split():
        if re.fullmatch("[A-Za-z]+", word) and word[0].upper() == word[0]:
            result += word[0].lower()
        else:
            return text
    return result


conn = psycopg2.connect(user='docker', password='docker',
                        host='89.208.85.17', port='5432')
cursor = conn.cursor()
role_tech = defaultdict(list)
beauty_name_pos = dict()
beauty_name_tech = dict()
cv_sim_pos = dict()

#TEXT_CV = " movie space go https movie space ru https github com go park mail ru kuragateam tinder c++ https github com amrion mcflurry chocolate python django https github com vorolga tp web androidjava https github com zdesbilaksenia studentsmap vk ex https park vk company curriculum program main golang postgres redis git linux docker grpc rest unit + voronovaolja yandex ru intermediate web "
#TEXT_CV = " machine learning engineer ++ developer + github com superaiyah fedorx safonovfedya gmail com codeforces fedorx moscow russia gpa c++ image meda center gui wxwidgets astra linux cmake vk ml ml c c++ dl school cnn alexnet vgg resnet densenet inseption segnet u net rcnn vae cvae java java git + gif code review tinkoff b online alias c++ alias online uml qt youtube best data science + c++ ii ii python numpy pandas matplotlib seaborn pytorch catboost scikit learn aiogram unittest ++ gtest cmake qt wxwidgets java linux sql ms sql mysql git ci cd team work "

def get_learned(text_cv: str, prof: str, n: int = 5) -> list[str]:
    techs = set(role_tech[prof])
    result = []

    for tech_p in techs:
        tech = tech_p[0]
        if " "+tech+" " in text_cv or " "+get_abbr(beauty_name_tech[tech])+" " in text_cv:
            result.append(beauty_name_tech[tech])
            if len(result) == n:
                break

    return list(set(result))

def get_to_learn(text_cv: str, prof: str, n: int = 5) -> list[str]:
    techs = set(role_tech[prof])
    result = []

    for tech_p in techs:
        tech = tech_p[0]
        if " "+tech+" " not in text_cv and " "+get_abbr(beauty_name_tech[tech])+" " not in text_cv:
            result.append(beauty_name_tech[tech])
            if len(result) == n:
                break

    return list(set(result))

def get_recommendation_cv(raw_text: str,  n_prof: int, n_techs: int = 10) -> list[dict]:
    text_cv = get_clean_text(raw_text)

    with conn.cursor() as cursor:
        result = []

        cursor.execute('SELECT * FROM technology_position')
        for elem in cursor:
            row = Row(*elem)
            clean_position = get_clean_text(row.name_position)
            if clean_position == "c developer" or clean_position == "c# developer":
                continue
            clean_technolohy = get_clean_text(row.name_technology)
            if not clean_technolohy or has_rus(row.name_technology):
                continue
            role_tech[clean_position].append((clean_technolohy, row.distance))
            beauty_name_pos[clean_position] = row.name_position
            beauty_name_tech[clean_technolohy] = row.name_technology

            # Подсчет сходства CV и профессии
            cv_sim_pos[clean_position] = 0
            for tech_p in role_tech[clean_position]:
                tech = tech_p[0]
                if get_clean_text(tech) in text_cv:
                    cv_sim_pos[clean_position] += 1
            cv_sim_pos[clean_position] /= len(role_tech[clean_position])

        for key in role_tech:
            role_tech[key] = sorted(list(set(role_tech[key])), key=lambda p: p[1], reverse=True)

        closed_prof = sorted(cv_sim_pos.items(), key=lambda p: p[1], reverse=True)

        for prof, prc in closed_prof[:n_prof]:
            res_tmp = {
                "profession": beauty_name_pos[prof],
                "simularity": prc,
                "learned": get_learned(text_cv, prof, n_techs),
                "to_learn": get_to_learn(text_cv, prof, n_techs)
            }
            result.append(res_tmp)

    return result
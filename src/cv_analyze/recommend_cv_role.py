from pydantic import BaseModel
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


def has_rus(text: str) -> bool:
    txt = re.findall('[А-яёЁ]+', text)
    if txt:
        return True
    return False


def get_clean_text(text: str) -> str:
    text = re.sub("[^0-9A-Za-zа-яА-ЯЁё\d\+# ]", " ", text)
    text = re.sub("\s+", " ", text).strip().lower()
    return text


def get_recommend(input_cv: str,
                  role: str,
                  n: int,
                  syn: dict[str, str],
                  role_tech_dist: dict) -> Recommend:
    cv_text = " " + get_clean_text(input_cv) + " "

    if role not in role_tech_dist:
        return Recommend(recommend=[{
        "learned": [],
        "to_learn": []
    }])

    role_techs = role_tech_dist[role].keys()
    learned = list()
    to_learn = list()

    for tech in role_techs:
        if " "+get_clean_text(tech)+" " in cv_text:
            learned.append(tech)
        else:
            to_learn.append(tech)
    used_techs = []
    learned_ans = []
    to_learn_ans = []
    for tech in learned:
        if tech == "Ozone":
            continue
        if tech in syn:
            new_tech = syn[tech]
        else:
            new_tech = tech
        if get_clean_text(tech) not in used_techs:
            learned_ans.append((new_tech, role_tech_dist[role][tech]))
            used_techs.append(get_clean_text(new_tech))
    for tech in to_learn:
        if has_rus(tech):
            continue
        if tech in syn:
            new_tech = syn[tech]
        else:
            new_tech = tech
        if get_clean_text(tech) not in used_techs:
            to_learn_ans.append((new_tech, role_tech_dist[role][tech]))
            used_techs.append(get_clean_text(new_tech))

    to_learn_ans = sorted(to_learn_ans, key=lambda x: -x[1])
    learned_ans = sorted(learned_ans, key=lambda x: -x[1])
    print(to_learn_ans[:10])
    print(learned_ans[:10])
    if to_learn_ans[0][0] == "Ozone":
        del to_learn_ans[0]

    learned_ans = list(map(lambda x: x[0], learned_ans[:min(n, len(to_learn_ans))]))
    to_learn_ans = list(map(lambda x: x[0], to_learn_ans[:min(n, len(to_learn_ans))]))

    return Recommend(recommend=[{
        "learned": learned_ans,
        "to_learn": to_learn_ans
    }])



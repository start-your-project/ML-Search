from psycopg2.pool import SimpleConnectionPool
from Levenshtein import distance
from src.cv_analyze.recommend_cv_role import Row, has_rus, get_clean_text
from dataclasses import dataclass

@dataclass
class TechSynRow():
    id: int
    bad_name: str
    true_name: str

def get_recommend_tech(input: str, n: int, postgres_pool: SimpleConnectionPool) -> list[str]:
    result = []
    input_norm = get_clean_text(input)
    syn_bad_good = dict()

    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM technology_synonyms')
        for elem in cursor:
            row = TechSynRow(*elem)
            if not has_rus(row.bad_name):
                syn_bad_good[row.bad_name] = row.true_name
                syn_bad_good[row.true_name] = row.true_name
        cursor.close()
        postgres_pool.putconn(connection)
        print("PostgreSQL connection is returned to the pool")
    used_tech = set()
    for bad_name in set(syn_bad_good.keys()):
        if bad_name not in used_tech:
            result.append((bad_name, distance(input_norm, get_clean_text(bad_name))))
            used_tech.add(bad_name)
    result = list(set(result))
    n = min(n, len(result))
    result = sorted(result, key=lambda x: x[1])
    result_bad_names = list(map(lambda x: x[0], result))
    result_good_names = [syn_bad_good[bad_name] for bad_name in result_bad_names]
    ans = []
    for elem in result_good_names:
        if elem not in ans:
            ans.append(elem)
        if len(ans) == n:
            break
    return ans

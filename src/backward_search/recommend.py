from psycopg2.pool import SimpleConnectionPool
from Levenshtein import distance
from src.cv_analyze.recommend_cv_role import Row, has_rus, get_clean_text


def get_recommend_tech(input: str, n: int, postgres_pool: SimpleConnectionPool) -> list[str]:
    result = []
    input_norm = get_clean_text(input)

    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM technology_position')
        for elem in cursor:
            row = Row(*elem)
            if not has_rus(row.name_technology):
                result.append((row.name_technology, distance(input_norm, get_clean_text(row.name_technology))))
        cursor.close()
        postgres_pool.putconn(connection)
        print("PostgreSQL connection is returned to the pool")

    result = list(set(result))
    n = min(n, len(result))
    result = sorted(result, key=lambda x: x[1])
    result_prof = list(map(lambda x: x[0], result[:n]))
    return result_prof

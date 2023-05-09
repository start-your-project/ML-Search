from psycopg2.pool import SimpleConnectionPool
from collections import defaultdict


def load_synonyms(postgres_pool: SimpleConnectionPool) -> dict[str, str]:
    syn = dict()
    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM technology_synonyms')
        for elem in cursor:
            bad_name, true_name = elem[1], elem[2]
            syn[bad_name] = true_name
            syn[true_name] = true_name
        cursor.close()
        postgres_pool.putconn(connection)
        print("PostgreSQL connection is returned to the pool")
    else:
        print("Error creation connection")
    return syn

def load_freq(postgres_pool: SimpleConnectionPool, synUPD: dict[str, str]) -> dict:
    freq = defaultdict(dict)
    connection = postgres_pool.getconn()
    if connection:
        print("Connection is established")
        cursor = connection.cursor()
        cursor.execute('SELECT name_technology, name_position, distance FROM technology_position')
        for elem in cursor:
            tech, role, dist = elem[0], elem[1], elem[2]
            freq[role][tech] = float(dist)
            synUPD[tech] = tech
        cursor.close()
        postgres_pool.putconn(connection)
        print("PostgreSQL connection is returned to the pool")
    else:
        print("Error creation connection")
    return freq


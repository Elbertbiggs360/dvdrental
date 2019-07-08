from enum import Enum, auto, unique

@unique
class Ratings(Enum):
    PG = auto()
    G = auto()
    NC17 = auto()
    PG13 = auto()

def create_ratings(cur, conn, list):
    cur.execute(f"CREATE TYPE mpaa_ratings as ENUM ('PG', 'G', 'NC-17', 'PG-13')")
    if conn.commit():
        return True
    return False

def create_vector_doc(cur, conn, movie):
    cur.execute(f"SELECT max(film_id) FROM film WHERE title='{movie['title']}'")
    new_film_id = cur.fetchone()[0]
    cur.execute(
        f"""
            SELECT (title, description) AS DOCUMENT
            FROM film where film_id = {new_film_id}
        """
    )
    res = cur.fetchone()
    full_text = res[0].replace('"', "'")
    cur.execute(
        f"""
        UPDATE film
        SET fulltext = to_tsvector({full_text})
        WHERE
            film_id='{new_film_id}'
        """
    )
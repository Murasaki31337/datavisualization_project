import psycopg2, os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)

cur = conn.cursor()

with open("queries.sql", "r", encoding="utf-8") as f:
    sql = f.read()

cur.execute(sql)  # ⚠ works if queries.sql has ONE query
print(cur.fetchall())

cur.close()
conn.close()

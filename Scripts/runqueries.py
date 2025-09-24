import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build absolute path to queries.sql (in same folder as this script)
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_file = os.path.join(base_dir, "queries.sql")

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)
cur = conn.cursor()

# Read SQL file
with open(sql_file, "r", encoding="utf-8") as f:
    sql_script = f.read()

# Split queries by semicolon
queries = [q.strip() for q in sql_script.split(";") if q.strip()]

for i, query in enumerate(queries, start=1):
    print(f"\n Running Query {i}:\n{query}\n")
    try:
        cur.execute(query)
        if cur.description:  # if query returns rows
            rows = cur.fetchall()
            # Print first 10 rows for readability
            for row in rows[:10]:
                print(row)
            if len(rows) > 10:
                print(f"... ({len(rows)} rows total)")
        else:
            print("✅ Query executed successfully (no result returned).")
    except Exception as e:
        print(f" Error in Query {i}: {e}")
        conn.rollback()
    else:
        conn.commit()

cur.close()
conn.close()
print("\nAll queries finished.")

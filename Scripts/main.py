import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv


load_dotenv()  # loads .env file

conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)

def q(sql):
    return pd.read_sql(sql, conn)


# 1. Top 10 players by rating
print("\nTop 10 players by rating (min 100 rounds):")
print(q("""
SELECT player_name, team, ROUND(AVG(rating)::numeric,2) AS avg_rating, SUM(rounds) AS total_rounds
FROM player_stats
GROUP BY player_name, team
HAVING SUM(rounds) >= 100
ORDER BY avg_rating DESC
LIMIT 10;
"""))

# 2. Clutch success
print("\nTop 10 players by clutch success:")
print(q("""
SELECT player_name,
       SUM(clutches_won) AS won,
       SUM(clutches_attempted) AS attempted,
       ROUND(100.0*SUM(clutches_won)/NULLIF(SUM(clutches_attempted),0),2) AS clutch_pct
FROM player_stats
GROUP BY player_name
HAVING SUM(clutches_attempted) >= 10
ORDER BY clutch_pct DESC
LIMIT 10;
"""))

# 3. Average ACS per team
print("\nAverage ACS per team:")
print(q("""
SELECT team, ROUND(AVG(acs)::numeric,1) AS avg_acs
FROM player_stats
GROUP BY team
ORDER BY avg_acs DESC
LIMIT 10;
"""))

# 4. Agent usage on Bind
print("\nTop 10 agents by utilization on Bind:")
print(q("""
SELECT agent_name, (map_utilizations->>'Bind')::float AS bind_util
FROM agents_stats
WHERE map_utilizations ? 'Bind'
ORDER BY bind_util DESC
LIMIT 10;
"""))

conn.close()

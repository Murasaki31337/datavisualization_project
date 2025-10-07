import os
import time
import random
import psycopg2
from dotenv import load_dotenv

# Load DB credentials
load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)
conn.autocommit = True

# --- Step 1: ensure table exists ---
with conn.cursor() as cur:
    cur.execute("""
    CREATE TABLE IF NOT EXISTS team_acs_stream (
        id       bigserial PRIMARY KEY,
        ts       timestamptz NOT NULL DEFAULT now(),
        team     text NOT NULL,
        avg_acs  numeric(10,2) NOT NULL CHECK (avg_acs >= 0)
    );
    """)

# --- Step 2: fetch all real team names ---
with conn.cursor() as cur:
    cur.execute("""
        SELECT DISTINCT player_team
        FROM detailed_matches_player_stats
        WHERE player_team IS NOT NULL
    """)
    TEAMS = [r[0] for r in cur.fetchall()]

if not TEAMS:
    TEAMS = ["Team Alpha", "Team Beta", "Team Gamma"]

# --- Step 3: initialize base values per team ---
last_values = {team: random.uniform(180, 260) for team in TEAMS}

print(f"Streaming ACS for {len(TEAMS)} teams...")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        rows = []
        for team in TEAMS:
            # random walk per team
            step = random.uniform(-10, 10)
            new_val = max(0, round(last_values[team] + step, 2))
            last_values[team] = new_val
            rows.append((team, new_val))

        # batch insert for all teams this tick
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO team_acs_stream (team, avg_acs) VALUES (%s, %s)", rows
            )

        print(f"[{time.strftime('%H:%M:%S')}] Inserted {len(rows)} rows")
        time.sleep(10)  # wait before next update (5–20s OK)
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    conn.close()

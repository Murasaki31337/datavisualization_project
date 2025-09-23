import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT")
)

cur = conn.cursor()

# Drop tables if they exist (optional, for re-runs)
drop_sql = """
DROP TABLE IF EXISTS detailed_matches_player_stats CASCADE;
DROP TABLE IF EXISTS detailed_matches_maps CASCADE;
DROP TABLE IF EXISTS detailed_matches_overview CASCADE;
DROP TABLE IF EXISTS performance_data CASCADE;
DROP TABLE IF EXISTS economy_data CASCADE;
DROP TABLE IF EXISTS event_info CASCADE;
DROP TABLE IF EXISTS maps_stats CASCADE;
DROP TABLE IF EXISTS agents_stats CASCADE;
DROP TABLE IF EXISTS player_stats CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
"""
cur.execute(drop_sql)

# Create schema (tables)
create_sql = """
CREATE TABLE matches (
    match_id INT PRIMARY KEY,
    date TEXT,
    time TEXT,
    team1 TEXT,
    score1 INT,
    team2 TEXT,
    score2 INT,
    score TEXT,
    winner TEXT,
    status TEXT,
    week TEXT,
    stage TEXT
);

CREATE TABLE player_stats (
    player TEXT,
    player_name TEXT,
    team TEXT,
    player_id TEXT,
    agents_count INT,
    agents TEXT,
    rounds INT,
    rating FLOAT,
    acs FLOAT,
    kd_ratio FLOAT,
    kast FLOAT,
    adr FLOAT,
    kpr FLOAT,
    apr FLOAT,
    fkpr FLOAT,
    fdpr FLOAT,
    hs_percent FLOAT,
    cl_percent FLOAT,
    clutches_won INT,
    clutches_attempted INT,
    k_max INT,
    kills INT,
    deaths INT,
    assists INT,
    first_kills INT,
    first_deaths INT,
    match_id INT REFERENCES matches(match_id)
);

CREATE TABLE agents_stats (
    agent_name TEXT PRIMARY KEY,
    total_utilization FLOAT,
    map_utilizations JSON
);

CREATE TABLE maps_stats (
    map_name TEXT PRIMARY KEY,
    times_played INT,
    attack_win_percent FLOAT,
    defense_win_percent FLOAT
);

CREATE TABLE event_info (
    url TEXT,
    title TEXT,
    subtitle TEXT,
    dates TEXT,
    prize_pool TEXT,
    location TEXT
);

CREATE TABLE economy_data (
    map TEXT,
    team TEXT,
    match_id INT REFERENCES matches(match_id),
    pistol_won TEXT,
    eco_won TEXT,
    semi_eco_won TEXT,
    semi_buy_won TEXT,
    full_buy_won TEXT
);

CREATE TABLE performance_data (
    match_id INT REFERENCES matches(match_id),
    map TEXT,
    player TEXT,
    team TEXT,
    agent TEXT,
    two_k INT,
    three_k INT,
    four_k INT,
    five_k INT,
    clutch_1v1 INT,
    clutch_1v2 INT,
    clutch_1v3 INT,
    clutch_1v4 INT,
    clutch_1v5 INT,
    econ FLOAT,
    pl FLOAT,
    de FLOAT
);

CREATE TABLE detailed_matches_overview (
    match_id INT REFERENCES matches(match_id),
    match_title TEXT,
    event TEXT,
    date TEXT,
    format TEXT,
    teams TEXT,
    score TEXT,
    maps_played INT,
    patch TEXT,
    pick_ban_info TEXT
);

CREATE TABLE detailed_matches_maps (
    match_id INT REFERENCES matches(match_id),
    map_name TEXT REFERENCES maps_stats(map_name),
    map_order INT,
    score TEXT,
    winner TEXT,
    duration TEXT,
    picked_by TEXT
);

CREATE TABLE detailed_matches_player_stats (
    match_id INT REFERENCES matches(match_id),
    event_name TEXT,
    event_stage TEXT,
    match_date TEXT,
    team1 TEXT,
    team2 TEXT,
    score_overall TEXT,
    player_name TEXT,
    player_id TEXT,
    player_team TEXT,
    stat_type TEXT,
    agent TEXT REFERENCES agents_stats(agent_name),
    rating FLOAT,
    acs FLOAT,
    k INT,
    d INT,
    a INT,
    kd_diff INT,
    kast FLOAT,
    adr FLOAT,
    hs_percent FLOAT,
    fk INT,
    fd INT,
    fk_fd_diff INT,
    map_name TEXT REFERENCES maps_stats(map_name),
    map_winner TEXT
);
"""

cur.execute(create_sql)
conn.commit()

cur.close()
conn.close()

print("✅ All tables created successfully!")

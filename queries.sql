-- 1. Total number of matches in the tournament
SELECT COUNT(*) AS total_matches
FROM matches;

-- 2. Total number of unique players
SELECT COUNT(DISTINCT player_name) AS total_players
FROM player_stats;

-- 3. Top 10 players by average rating (min 100 rounds)
SELECT player_name, team, ROUND(AVG(rating)::numeric,2) AS avg_rating, SUM(rounds) AS total_rounds
FROM player_stats
GROUP BY player_name, team
HAVING SUM(rounds) >= 100
ORDER BY avg_rating DESC
LIMIT 10;

-- 4. Top 10 players by clutch success rate (min 10 attempts)
SELECT player_name,
SUM(clutches_won) AS won,
SUM(clutches_attempted) AS attempted,
ROUND(100.0*SUM(clutches_won)/NULLIF(SUM(clutches_attempted),0),2) AS clutch_pct
FROM player_stats
GROUP BY player_name
HAVING SUM(clutches_attempted) >= 10
ORDER BY clutch_pct DESC
LIMIT 10;

-- 5. Team standings by total matches won
SELECT winner AS team, COUNT(*) AS wins
FROM matches
GROUP BY winner
ORDER BY wins DESC;

-- 6. Average ACS (combat score) per team
SELECT team, ROUND(AVG(acs)::numeric,1) AS avg_acs
FROM player_stats
GROUP BY team
ORDER BY avg_acs DESC
LIMIT 10;

-- 7. Map popularity
SELECT map_name, COUNT(*) AS times_played
FROM detailed_matches_maps
GROUP BY map_name
ORDER BY times_played DESC;

-- 8. Map win distribution (how often picked team wins)
SELECT map_name,
COUNT(*) AS times_played,
COUNT(CASE WHEN winner = picked_by THEN 1 END) AS picked_team_wins,
ROUND((COUNT(CASE WHEN winner = picked_by THEN 1 END)::numeric / COUNT(*)::numeric) * 100, 2) 
AS picked_team_win_pct
FROM detailed_matches_maps
GROUP BY map_name
ORDER BY times_played DESC;

-- 9. Agent usage overall (most used agents)
SELECT agent_name, total_utilization
FROM agents_stats
ORDER BY total_utilization DESC
LIMIT 10;

-- 10. Agent usage on Bind (JSON extraction example)
SELECT agent_name, (map_utilizations->>'Bind')::float AS bind_util
FROM agents_stats
WHERE map_utilizations ? 'Bind'
ORDER BY bind_util DESC
LIMIT 10;

-- 11. Top players by kills
SELECT player_name, SUM(kills) AS total_kills
FROM player_stats
GROUP BY player_name
ORDER BY total_kills DESC
LIMIT 10;

-- 12. Event-level average rating
SELECT event_name, ROUND(AVG(rating)::numeric,2) AS avg_rating
FROM detailed_matches_player_stats
GROUP BY event_name
ORDER BY avg_rating DESC
LIMIT 15;

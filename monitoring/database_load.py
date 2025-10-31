import psycopg2, time, random

# ✅ Adjust your database credentials
conn = psycopg2.connect(
    host="localhost",
    database="valorant_tournament",
    user="postgres",
    password="Murasaki31337"
)

cur = conn.cursor()
print("🚀 Database stress test started...")

try:
    while True:
        # Simulate SELECTs
        cur.execute("SELECT generate_series(1, 1000)")
        _ = cur.fetchall()
        
        # Simulate inserts/updates
        cur.execute("CREATE TABLE IF NOT EXISTS test_stress (id SERIAL, val INT)")
        for _ in range(50):
            cur.execute("INSERT INTO test_stress (val) VALUES (%s)", (random.randint(1, 1000),))
        
        conn.commit()
        print("✅ Queries executed, sleeping 10s...")
        time.sleep(10)

except KeyboardInterrupt:
    print("🛑 Stress test stopped manually.")
finally:
    cur.close()
    conn.close()

import sqlite3
import json

db_path = r"c:\Users\ASUS\Videos\CareerAI\CareerMind-AI\backend\careermind.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print("=== TABLES IN CAREERMIND.DB ===")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
    cnt = cursor.fetchone()[0]
    print(f"{t}: {cnt} rows")

print("\n=== SAMPLE ROWS ===")
for t in tables:
    if t.startswith("alembic"):
        continue
    cursor.execute(f"SELECT * FROM `{t}` LIMIT 3")
    rows = cursor.fetchall()
    print(f"\n--- Table: {t} (Sample {len(rows)} rows) ---")
    for r in rows:
        d = dict(r)
        # truncate long strings
        for k, v in d.items():
            if isinstance(v, str) and len(v) > 100:
                d[k] = v[:100] + "... [truncated]"
        print(d)

conn.close()


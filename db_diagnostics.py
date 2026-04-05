import psycopg
from config import PG_CONN_STR

def check_db():
    with psycopg.connect(PG_CONN_STR) as conn:
        with conn.cursor() as cur:
            with open("db_diag_out.txt", "w", encoding="utf-8") as f:
                # 1. Check chapter distribution
                cur.execute("SELECT chapter, COUNT(*) FROM rag_cv_chunks GROUP BY chapter ORDER BY chapter")
                f.write("--- Chapter Counts ---\n")
                for r in cur.fetchall():
                    f.write(f"{r[0]}: {r[1]}\n")
                
                # 2. Check for "neural network" definition
                cur.execute("SELECT chapter, section, content FROM rag_cv_chunks WHERE content ILIKE '%neural network is%' OR content ILIKE '%define a neural network%' LIMIT 5")
                f.write("\n--- Definition Chunks ---\n")
                for r in cur.fetchall():
                    f.write(f"[{r[0]}] {r[1]}: {r[2][:150].strip()}...\n")
                
                # 3. Check for specific common intro text "Deep feedforward networks"
                cur.execute("SELECT chapter, section, content FROM rag_cv_chunks WHERE content ILIKE '%Deep feedforward networks%' LIMIT 3")
                f.write("\n--- Chapter 6 Intro ---\n")
                for r in cur.fetchall():
                    f.write(f"[{r[0]}] {r[1]}: {r[2][:150].strip()}...\n")

if __name__ == "__main__":
    check_db()

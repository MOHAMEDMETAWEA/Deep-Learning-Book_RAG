"""
fix_db.py
────────
One-off script to ensure the PostgreSQL schema is up-to-date with all missing columns
(like page_start, page_end, chapter, etc.).

Run this if you see "column does not exist" errors in the RAG pipeline.
"""

from config import PG_CONN_STR, EMBED_DIM
from db import init_db

if __name__ == "__main__":
    print(f"🔧 Starting database schema fix for: {PG_CONN_STR}")
    try:
        init_db(PG_CONN_STR, EMBED_DIM)
        print("✅ Database schema updated successfully!")
    except Exception as e:
        print(f"❌ Error updating database: {e}")

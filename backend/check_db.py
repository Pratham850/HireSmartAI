import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import settings

async def check_db_connection():
    print("=" * 60)
    print("HireSmart AI - Database Connection Diagnostic Utility")
    print("=" * 60)
    print(f"Configured DATABASE_URL: {settings.DATABASE_URL}\n")

    # Test Primary Database URL
    primary_url = settings.DATABASE_URL
    print(f"1. Attempting connection to primary database: {primary_url}")
    
    connect_args = {}
    if "sqlite" in primary_url:
        connect_args["check_same_thread"] = False

    try:
        test_engine = create_async_engine(primary_url, connect_args=connect_args)
        async with test_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            val = result.scalar()
            print(f"   [SUCCESS] Primary DB connection successful! (Ping test returned: {val})")

            # Check tables
            print("\n2. Checking existing database tables...")
            if "mysql" in primary_url:
                tables_res = await conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in tables_res.fetchall()]
            elif "postgresql" in primary_url:
                tables_res = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
                tables = [row[0] for row in tables_res.fetchall()]
            else: # sqlite
                tables_res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_res.fetchall()]
            
            print(f"   Found {len(tables)} table(s): {', '.join(tables) if tables else 'None'}")
        await test_engine.dispose()
        return

    except Exception as exc:
        print(f"   [FAILED] Primary DB connection failed.")
        print(f"   Error Details: {exc}")

    # Test Fallback SQLite Database
    fallback_url = "sqlite+aiosqlite:///./hiresmart_dev.db"
    print(f"\n3. Testing connection to fallback local SQLite database: {fallback_url}")
    try:
        fb_engine = create_async_engine(fallback_url, connect_args={"check_same_thread": False})
        async with fb_engine.connect() as conn:
            res = await conn.execute(text("SELECT 1"))
            print(f"   [SUCCESS] Local SQLite fallback DB is online and working!")
            tables_res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in tables_res.fetchall()]
            print(f"   Found {len(tables)} table(s) in SQLite: {', '.join(tables) if tables else 'None'}")
        await fb_engine.dispose()
    except Exception as exc:
        print(f"   [ERROR] Fallback SQLite connection failed: {exc}")

if __name__ == "__main__":
    asyncio.run(check_db_connection())

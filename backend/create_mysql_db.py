import pymysql
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings

def create_db_if_not_exists():
    url = settings.DATABASE_URL
    if "mysql" not in url:
        print("Not a MySQL DATABASE_URL. Skipping database creation.")
        return

    # Extract connection credentials
    # Format: mysql+aiomysql://user:password@host:port/dbname
    try:
        clean_url = url.split("://")[-1]
        user_pass, host_port_db = clean_url.split("@")
        user, password = user_pass.split(":", 1) if ":" in user_pass else (user_pass, "")
        
        if "/" in host_port_db:
            host_port, dbname = host_port_db.split("/", 1)
        else:
            host_port, dbname = host_port_db, "hiresmart_db"
            
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 3306

        print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()
        print(f"Creating database '{dbname}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[SUCCESS] MySQL database '{dbname}' is ready!")

    except Exception as exc:
        print(f"[FAILED] Failed to create database: {exc}")

if __name__ == "__main__":
    create_db_if_not_exists()

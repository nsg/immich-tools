import os

import psycopg2
import psycopg2.extras


class ImmichDatabase:

    def __init__(self) -> None:
        database = os.getenv("DB_DATABASE_NAME", "immich")
        host = os.getenv("DB_HOSTNAME", "127.0.0.1")
        username = os.getenv("DB_USERNAME", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        port = os.getenv("DB_PORT", 5432)

        self.conn = psycopg2.connect(
            database=database,
            host=host,
            user=username,
            password=password,
            port=port)

        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def list_users(self):
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def get_asset_checksum(self, checksum):
        checksum = f"\\x{checksum}"
        self.cursor.execute("SELECT id FROM assets WHERE checksum = %s", (checksum,))
        return self.cursor.fetchall()

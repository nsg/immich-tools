import os
import base64

import psycopg2
import psycopg2.extras


class ImmichDatabase:

    database: str
    host: str
    username: str
    password: str
    port: int

    def __init__(self) -> None:
        self.database = os.getenv("DB_DATABASE_NAME", "immich")
        self.host = os.getenv("DB_HOSTNAME", "127.0.0.1")
        self.username = os.getenv("DB_USERNAME", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.port = int(os.getenv("DB_PORT", 5432))

    def query(self, sql: str, args: tuple = ()):
        r = []
        conn = psycopg2.connect(
            database=self.database,
            host=self.host,
            user=self.username,
            password=self.password,
            port=self.port,
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, args)
        if cursor.rowcount > 0:
            for row in cursor:
                r.append(dict(row))
        cursor.close()
        conn.close()
        return r

    def get_old_hashes(self, hash, user_id, user_path):
        res = self.query(
            """
            SELECT id FROM hasher_scanned_files
            WHERE checksum <> %s AND asset_path = %s AND user_id = %s
            """,
            (hash, user_path, user_id),
        )
        r = []
        for asset in res:
            r.append(asset["id"])
        return r

    def delete_asset_by_id(self, id):
        self.query(
            """
            DELETE FROM hasher_scanned_files
            WHERE id = %s;
            """,
            (id,),
        )

    def set_asset_checksum(self, hash, user_id, user_path):
        try:
            self.query(
                """
                INSERT INTO hasher_scanned_files(user_id, asset_path, checksum, changed_on)
                VALUES(%s, %s, %s, NOW());
                """,
                (user_id, user_path, hash),
            )
        except psycopg2.errors.UniqueViolation:
            pass

    def local_file(self, hash, user_id):
        res = self.query(
            "SELECT * FROM hasher_scanned_files WHERE checksum = %s AND user_id = %s",
            (hash, user_id)
        )
        r = []
        for asset in res:
            r.append(
                {
                    "id": asset["id"],
                    "path": asset["asset_path"],
                    "changed": asset["changed_on"],
                }
            )
        return {"assets": r, "count": len(r)}

    def provision_database(self):
        self.query(
            """
            CREATE TABLE IF NOT EXISTS hasher_scanned_files (
                id INT GENERATED ALWAYS AS IDENTITY,
                user_id VARCHAR(255) NOT NULL,
                asset_path TEXT NOT NULL,
                checksum BYTEA,
                changed_on TIMESTAMP(6) NOT NULL,
                UNIQUE(asset_path, checksum)
            );
        """
        )

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

    def list_users(self):
        r = []
        for user in self.query("SELECT * FROM users"):
            r.append(user["id"])
        return r

    def get_externalfile_by_checksum(self, checksum):
        q = self.query(
            "SELECT * FROM hasher_scanned_files WHERE checksum = %s", (checksum,)
        )
        r = []
        for asset in q:
            r.append(
                {
                    "id": asset["id"],
                    "user_id": asset["user_id"],
                    "path": asset["asset_path"],
                    "changed": asset["changed_on"],
                }
            )
        return {"assets": r, "count": len(r)}

    def get_asset_checksum(self, checksum, user_id):
        checksum = f"\\x{checksum}"

        if user_id:
            q = self.query(
                'SELECT id, "userId" FROM assets WHERE checksum = %s AND "userId" = %s',
                (checksum, user_id),
            )
        else:
            q = self.query(
                'SELECT id, "userId" FROM assets WHERE checksum = %s', (checksum,)
            )

        r = []
        for asset in q:
            r.append({"asset_id": asset["id"], "user_id": asset["userId"]})
        return {"assets": r, "count": len(r)}

    def list_last_deleted_assets(self):
        q = self.query(
            """
            SELECT asset_id, user_id, checksum, changed_on
                FROM assets_delete_audits
                WHERE changed_on BETWEEN NOW() - INTERVAL '2 MINUTES' AND NOW()
            """
        )
        r = []
        for deleted in q:
            row = {
                "id": deleted["asset_id"],
                "user_id": deleted["user_id"],
                "checksum": bytes(deleted["checksum"]).hex(),
                "changed": deleted["changed_on"],
            }
            r.append(row)
        return r

    def provision_delete_trigger(self):
        self.query(
            """
            CREATE TABLE IF NOT EXISTS assets_delete_audits (
                id INT GENERATED ALWAYS AS IDENTITY,
                asset_id UUID NOT NULL,
                user_id VARCHAR(256) NULL,
                checksum BYTEA,
                changed_on TIMESTAMP(6) NOT NULL
            );
        """
        )

        self.query(
            """
            CREATE OR REPLACE FUNCTION log_assets_delete_audits()
                RETURNS TRIGGER
                LANGUAGE PLPGSQL
                AS
            $$
            BEGIN
                INSERT INTO assets_delete_audits(asset_id, user_id, checksum, changed_on)
                VALUES(OLD.id, OLD."userId", OLD.checksum, NOW());
                RETURN OLD;
            END;
            $$
        """
        )

        self.query(
            """
            CREATE OR REPLACE TRIGGER trigger_assets_delete_audits
            BEFORE DELETE ON assets
            FOR EACH ROW
            EXECUTE PROCEDURE log_assets_delete_audits()
        """
        )

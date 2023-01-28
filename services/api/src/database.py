import os
import base64

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


    def list_users(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM users")
        r = []
        for user in cursor:
            r.append(user['id'])
        cursor.close()
        return r

    def get_asset_checksum(self, checksum):
        checksum = f"\\x{checksum}"
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT id FROM assets WHERE checksum = %s", (checksum,))
        r = []
        for asset in cursor:
            r.append(asset['id'])
        cursor.close()
        return { "assets": r, "count": len(r) }


    def list_deleted_assets_last_n_minutes(self, minutes):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT asset_id, checksum, changed_on
                FROM assets_delete_audits
                WHERE changed_on > (NOW() - interval '%s minutes')
            """, (minutes,))
        r = []
        for deleted in cursor:
            row = {
                "id": deleted["asset_id"],
                "checksum": bytes(deleted['checksum']).hex(),
                "changed": deleted["changed_on"]
            }
            r.append(row)
        cursor.close()
        return r

    def provision_delete_trigger(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets_delete_audits (
                id INT GENERATED ALWAYS AS IDENTITY,
                asset_id UUID NOT NULL,
                checksum BYTEA,
                changed_on TIMESTAMP(6) NOT NULL
            );
        """)

        cursor.execute("""
            CREATE OR REPLACE FUNCTION log_assets_delete_audits()
                RETURNS TRIGGER
                LANGUAGE PLPGSQL
                AS
            $$
            BEGIN
                INSERT INTO assets_delete_audits(asset_id,checksum,changed_on)
                VALUES(OLD.id, OLD.checksum, NOW());
                RETURN OLD;
            END;
            $$
        """)

        cursor.execute("""
            CREATE OR REPLACE TRIGGER trigger_assets_delete_audits
            BEFORE DELETE ON assets
            FOR EACH ROW
            EXECUTE PROCEDURE log_assets_delete_audits()
        """)

        cursor.close()
        self.conn.commit()

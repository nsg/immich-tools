import psycopg2
import psycopg2.extras


class ImmichDatabase:
    def __init__(self, database, host, username, password, port) -> None:

        self.conn = psycopg2.connect(
            database=database, host=host, user=username, password=password, port=port
        )

    def get_old_hashes(self, hash, user_id, user_path):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            SELECT id FROM hasher_scanned_files
            WHERE checksum <> %s AND asset_path = %s AND user_id = %s
            """,
            (hash, user_path, user_id),
        )
        r = []
        for asset in cursor:
            r.append(asset["id"])
        cursor.close()
        return r

    def delete_asset_by_id(self, id):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            """
            DELETE FROM hasher_scanned_files
            WHERE id = %s;
            """,
            (id,),
        )

        cursor.close()
        self.conn.commit()

    def set_asset_checksum(self, hash, user_id, user_path):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cursor.execute(
                """
                INSERT INTO hasher_scanned_files(user_id, asset_path, checksum, changed_on)
                VALUES(%s, %s, %s, NOW());
                """,
                (user_id, user_path, hash),
            )
        except psycopg2.errors.UniqueViolation:
            pass

        cursor.close()
        self.conn.commit()

    def provision_database(self):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
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

        cursor.close()
        self.conn.commit()

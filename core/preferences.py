import sqlite3
from pathlib import Path

from core.database import DEFAULT_DB_PATH


class PreferencesManager:
    def __init__(self, db_path: Path | str | None = None) -> None:
        """Initialize the PreferencesManager.

        Args:
            db_path: Path to the SQLite database file. If None, uses the default path.
        """
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._ensure_database()

    def _ensure_database(self) -> None:
        """Ensure the database and table exist."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self._db_path)

    def get(self, key: str) -> str | None:
        """Get a preference value by key.

        Args:
            key: The preference key.

        Returns:
            The preference value, or None if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM preferences WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        """Set a preference value.

        Args:
            key: The preference key.
            value: The preference value.
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO preferences (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            conn.commit()

    def delete(self, key: str) -> bool:
        """Delete a preference by key.

        Args:
            key: The preference key.

        Returns:
            True if a preference was deleted, False if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM preferences WHERE key = ?",
                (key,),
            )
            conn.commit()
            return cursor.rowcount > 0


_preferences_manager: PreferencesManager | None = None


def get_preferences_manager() -> PreferencesManager:
    """Get the global PreferencesManager instance.

    Returns:
        The global PreferencesManager singleton.
    """
    global _preferences_manager
    if _preferences_manager is None:
        _preferences_manager = PreferencesManager()
    return _preferences_manager

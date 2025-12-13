import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

DEFAULT_DB_PATH = Path.home() / ".cache" / "bab" / "history.db"


class HistoryItem(NamedTuple):
    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: str  # ISO 8601 format


class HistoryManager:
    def __init__(self, db_path: Path | str | None = None) -> None:
        """Initialize the HistoryManager.

        Args:
            db_path: Path to the SQLite database file. If None, uses the default path.
        """
        self._db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._ensure_database()

    def _ensure_database(self) -> None:
        """Ensure the database and table exist."""
        # Create parent directories if they don't exist
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id TEXT PRIMARY KEY,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(self._db_path)

    def create(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
    ) -> HistoryItem:
        """Create a new history entry.

        Args:
            source_text: The original text.
            translated_text: The translated text.
            source_lang: Source language NLLB code.
            target_lang: Target language NLLB code.

        Returns:
            The created HistoryItem.
        """
        item_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO history (id, source_text, translated_text, source_lang, target_lang, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    source_text,
                    translated_text,
                    source_lang,
                    target_lang,
                    timestamp,
                ),
            )
            conn.commit()

        return HistoryItem(
            id=item_id,
            source_text=source_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            timestamp=timestamp,
        )

    def find_by_content(
        self,
        source_text: str,
        source_lang: str,
        target_lang: str,
    ) -> HistoryItem | None:
        """Find an existing history entry by source text and language pair.

        Args:
            source_text: The original text.
            source_lang: Source language NLLB code.
            target_lang: Target language NLLB code.

        Returns:
            The matching HistoryItem if found, None otherwise.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, source_text, translated_text, source_lang, target_lang, timestamp
                FROM history
                WHERE source_text = ? AND source_lang = ? AND target_lang = ?
                """,
                (source_text, source_lang, target_lang),
            )
            row = cursor.fetchone()

        return HistoryItem(*row) if row else None

    def list_all(self) -> list[HistoryItem]:
        """List all history entries, sorted by timestamp (newest first).

        Returns:
            List of HistoryItem objects.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, source_text, translated_text, source_lang, target_lang, timestamp
                FROM history
                ORDER BY timestamp DESC
                """
            )
            rows = cursor.fetchall()

        return [HistoryItem(*row) for row in rows]

    def delete(self, item_id: str) -> bool:
        """Delete a history entry by ID.

        Args:
            item_id: The ID of the entry to delete.

        Returns:
            True if an entry was deleted, False if no entry was found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM history WHERE id = ?",
                (item_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """Delete all history entries.

        Returns:
            The number of entries deleted.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM history")
            conn.commit()
            return cursor.rowcount


_history_manager: HistoryManager | None = None


def get_history_manager() -> HistoryManager:
    """Get the global HistoryManager instance.

    Returns:
        The global HistoryManager singleton.
    """
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager()
    return _history_manager


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
        # Create parent directories if they don't exist
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

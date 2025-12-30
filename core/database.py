import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

DEFAULT_DB_PATH = Path.home() / ".cache" / "bab" / "saved_translations.db"


class SavedTranslation(NamedTuple):
    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: str  # ISO 8601 format


class SavedTranslationManager:
    def __init__(self, db_path: Path | str | None = None) -> None:
        """Initialize the SavedTranslationManager.

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
                CREATE TABLE IF NOT EXISTS saved_translations (
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
    ) -> SavedTranslation:
        """Create a new saved translation entry.

        Args:
            source_text: The original text.
            translated_text: The translated text.
            source_lang: Source language NLLB code.
            target_lang: Target language NLLB code.

        Returns:
            The created SavedTranslation.
        """
        item_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO saved_translations (id, source_text, translated_text, source_lang, target_lang, timestamp)
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

        return SavedTranslation(
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
    ) -> SavedTranslation | None:
        """Find an existing saved translation by source text and language pair.

        Args:
            source_text: The original text.
            source_lang: Source language NLLB code.
            target_lang: Target language NLLB code.

        Returns:
            The matching SavedTranslation if found, None otherwise.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, source_text, translated_text, source_lang, target_lang, timestamp
                FROM saved_translations
                WHERE source_text = ? AND source_lang = ? AND target_lang = ?
                """,
                (source_text, source_lang, target_lang),
            )
            row = cursor.fetchone()

        return SavedTranslation(*row) if row else None

    def list_all(self) -> list[SavedTranslation]:
        """List all saved translations, sorted by timestamp (newest first).

        Returns:
            List of SavedTranslation objects.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, source_text, translated_text, source_lang, target_lang, timestamp
                FROM saved_translations
                ORDER BY timestamp DESC
                """
            )
            rows = cursor.fetchall()

        return [SavedTranslation(*row) for row in rows]

    def delete(self, item_id: str) -> bool:
        """Delete a saved translation by ID.

        Args:
            item_id: The ID of the entry to delete.

        Returns:
            True if an entry was deleted, False if no entry was found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM saved_translations WHERE id = ?",
                (item_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self) -> int:
        """Delete all saved translations.

        Returns:
            The number of entries deleted.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM saved_translations")
            conn.commit()
            return cursor.rowcount


_saved_translation_manager: SavedTranslationManager | None = None


def get_saved_translation_manager() -> SavedTranslationManager:
    """Get the global SavedTranslationManager instance.

    Returns:
        The global SavedTranslationManager singleton.
    """
    global _saved_translation_manager
    if _saved_translation_manager is None:
        _saved_translation_manager = SavedTranslationManager()
    return _saved_translation_manager

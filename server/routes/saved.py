"""Saved translations API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database import get_saved_translation_manager

router = APIRouter(prefix="/saved", tags=["saved"])


class SavedTranslationCreate(BaseModel):
    """Request model for creating a saved translation."""

    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str


class SavedTranslationResponse(BaseModel):
    """Response model for a saved translation."""

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: str


class SavedTranslationsListResponse(BaseModel):
    """Response model for listing saved translations."""

    items: list[SavedTranslationResponse]


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool
    message: str


class SavedTranslationCheckResponse(BaseModel):
    """Response model for checking if a saved translation exists."""

    exists: bool
    id: str | None = None


@router.get("/check", response_model=SavedTranslationCheckResponse)
async def check_saved_translation(
    source_text: str,
    source_lang: str,
    target_lang: str,
) -> SavedTranslationCheckResponse:
    """Check if a translation is already saved.

    Returns whether the entry exists and its ID if found.
    """
    manager = get_saved_translation_manager()

    existing = manager.find_by_content(
        source_text=source_text,
        source_lang=source_lang,
        target_lang=target_lang,
    )

    if existing:
        return SavedTranslationCheckResponse(exists=True, id=existing.id)

    return SavedTranslationCheckResponse(exists=False)


@router.get("", response_model=SavedTranslationsListResponse)
async def list_saved_translations() -> SavedTranslationsListResponse:
    """List all saved translations.

    Returns saved translations sorted by timestamp, newest first.
    """
    manager = get_saved_translation_manager()
    items = manager.list_all()

    return SavedTranslationsListResponse(
        items=[
            SavedTranslationResponse(
                id=item.id,
                source_text=item.source_text,
                translated_text=item.translated_text,
                source_lang=item.source_lang,
                target_lang=item.target_lang,
                timestamp=item.timestamp,
            )
            for item in items
        ]
    )


@router.post("", response_model=SavedTranslationResponse)
async def create_saved_translation(
    request: SavedTranslationCreate,
) -> SavedTranslationResponse:
    """Create a new saved translation.

    If an entry with the same source text, source language, and target language
    already exists, the existing entry is returned instead of creating a duplicate.
    """
    manager = get_saved_translation_manager()

    existing = manager.find_by_content(
        source_text=request.source_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )

    if existing:
        return SavedTranslationResponse(
            id=existing.id,
            source_text=existing.source_text,
            translated_text=existing.translated_text,
            source_lang=existing.source_lang,
            target_lang=existing.target_lang,
            timestamp=existing.timestamp,
        )

    item = manager.create(
        source_text=request.source_text,
        translated_text=request.translated_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )

    return SavedTranslationResponse(
        id=item.id,
        source_text=item.source_text,
        translated_text=item.translated_text,
        source_lang=item.source_lang,
        target_lang=item.target_lang,
        timestamp=item.timestamp,
    )


@router.delete("/{item_id}", response_model=DeleteResponse)
async def delete_saved_translation(item_id: str) -> DeleteResponse:
    """Delete a specific saved translation by ID."""
    manager = get_saved_translation_manager()

    deleted = manager.delete(item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Saved translation not found")

    return DeleteResponse(success=True, message="Saved translation deleted")


@router.delete("", response_model=DeleteResponse)
async def clear_saved_translations() -> DeleteResponse:
    """Delete all saved translations."""
    manager = get_saved_translation_manager()

    count = manager.clear_all()

    return DeleteResponse(success=True, message=f"Deleted {count} saved translations")

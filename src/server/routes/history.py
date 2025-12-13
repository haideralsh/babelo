"""History API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database import get_history_manager

router = APIRouter(prefix="/history", tags=["history"])


class HistoryItemCreate(BaseModel):
    """Request model for creating a history item."""

    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str


class HistoryItemResponse(BaseModel):
    """Response model for a history item."""

    id: str
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    timestamp: str


class HistoryListResponse(BaseModel):
    """Response model for listing history items."""

    items: list[HistoryItemResponse]


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool
    message: str


@router.get("", response_model=HistoryListResponse)
async def list_history() -> HistoryListResponse:
    """List all translation history items.

    Returns history items sorted by timestamp, newest first.
    """
    manager = get_history_manager()
    items = manager.list_all()

    return HistoryListResponse(
        items=[
            HistoryItemResponse(
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


@router.post("", response_model=HistoryItemResponse)
async def create_history(request: HistoryItemCreate) -> HistoryItemResponse:
    """Create a new translation history item.

    If an entry with the same source text, source language, and target language
    already exists, the existing entry is returned instead of creating a duplicate.
    """
    manager = get_history_manager()

    existing = manager.find_by_content(
        source_text=request.source_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )

    if existing:
        return HistoryItemResponse(
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

    return HistoryItemResponse(
        id=item.id,
        source_text=item.source_text,
        translated_text=item.translated_text,
        source_lang=item.source_lang,
        target_lang=item.target_lang,
        timestamp=item.timestamp,
    )


@router.delete("/{item_id}", response_model=DeleteResponse)
async def delete_history_item(item_id: str) -> DeleteResponse:
    """Delete a specific history item by ID."""
    manager = get_history_manager()

    deleted = manager.delete(item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="History item not found")

    return DeleteResponse(success=True, message="History item deleted")


@router.delete("", response_model=DeleteResponse)
async def clear_history() -> DeleteResponse:
    """Delete all history items."""
    manager = get_history_manager()

    count = manager.clear_all()

    return DeleteResponse(success=True, message=f"Deleted {count} history items")

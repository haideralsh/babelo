"""Preferences API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.preferences import get_preferences_manager

router = APIRouter(prefix="/preferences", tags=["preferences"])


class PreferenceValue(BaseModel):
    """Request/Response model for preference value."""

    value: str


class PreferenceResponse(BaseModel):
    """Response model for a preference."""

    key: str
    value: str


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool
    message: str


@router.get("/{key}", response_model=PreferenceResponse)
async def get_preference(key: str) -> PreferenceResponse:
    """Get a preference value by key.

    Args:
        key: The preference key.

    Raises:
        HTTPException: If the preference is not found.
    """
    manager = get_preferences_manager()
    value = manager.get(key)

    if value is None:
        raise HTTPException(status_code=404, detail="Preference not found")

    return PreferenceResponse(key=key, value=value)


@router.put("/{key}", response_model=PreferenceResponse)
async def set_preference(key: str, request: PreferenceValue) -> PreferenceResponse:
    """Set or update a preference value.

    Args:
        key: The preference key.
        request: The preference value to set.
    """
    manager = get_preferences_manager()
    manager.set(key, request.value)

    return PreferenceResponse(key=key, value=request.value)


@router.delete("/{key}", response_model=DeleteResponse)
async def delete_preference(key: str) -> DeleteResponse:
    """Delete a preference by key.

    Args:
        key: The preference key.

    Raises:
        HTTPException: If the preference is not found.
    """
    manager = get_preferences_manager()
    deleted = manager.delete(key)

    if not deleted:
        raise HTTPException(status_code=404, detail="Preference not found")

    return DeleteResponse(success=True, message="Preference deleted")

"""Languages API routes."""

from fastapi import APIRouter

from core.model import LANGUAGE_CODES

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("")
async def list_languages() -> dict[str, dict[str, str]]:
    """List all supported languages.

    Returns a mapping of language names to their NLLB codes.
    """

    return {"languages": {name: code for name, code in sorted(LANGUAGE_CODES.items())}}

"""Languages API routes."""

from fastapi import APIRouter, HTTPException, Query

from core.model import DEFAULT_MODEL_ID, MODEL_REGISTRY, get_model_manager

router = APIRouter(prefix="/languages", tags=["languages"])


@router.get("")
async def list_languages(
    model_id: str = Query(
        default=DEFAULT_MODEL_ID,
        description="Model ID to get languages for",
    ),
) -> dict[str, dict[str, str] | str]:
    """List all supported languages for a model.

    Returns a mapping of language names to their codes for the specified model.

    Args:
        model_id: The model to get languages for. Defaults to 'nllb'.
    """
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    language_codes = manager.get_language_codes(model_id)

    return {
        "languages": {name: code for name, code in sorted(language_codes.items())},
        "model_id": model_id,
    }

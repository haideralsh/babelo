"""Translation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.model import DEFAULT_MODEL_ID, MODEL_REGISTRY, get_model_manager

router = APIRouter(prefix="/translate", tags=["translate"])


class TranslateRequest(BaseModel):
    """Request model for translation."""

    text: str
    source_language_code: str
    target_language_code: str
    model_id: str | None = None  # Defaults to 'nllb' if not specified


class TranslateResponse(BaseModel):
    """Response model for translation."""

    original_text: str
    translated_text: str
    source_language_code: str
    target_language_code: str
    model_id: str


@router.post("", response_model=TranslateResponse)
async def translate(request: TranslateRequest) -> TranslateResponse:
    """Translate text between languages.

    Translates the provided text from the source language to the target language
    using the specified model. The model must be downloaded first using the
    /model/download endpoint.

    Args:
        request: The translation request containing:
            - text: The text to translate
            - source_language_code: Source language code (format depends on model)
            - target_language_code: Target language code (format depends on model)
            - model_id: Model to use ('nllb' or 'translategemma'). Defaults to 'nllb'.

    Returns:
        The translated text along with language and model information.

    Raises:
        HTTPException: If the model is not downloaded or language code is not supported.
    """
    model_id = request.model_id or DEFAULT_MODEL_ID

    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    backend = manager.get_backend(model_id)

    if not backend.is_downloaded:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_id}' not downloaded. "
            f"Please call POST /model/download?model_id={model_id} first.",
        )

    # Validate language codes for the selected model
    valid_codes = set(backend.get_language_codes().values())

    src_lang = request.source_language_code
    tgt_lang = request.target_language_code

    if src_lang not in valid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language code for {model_id}: '{src_lang}'. "
            f"Use GET /languages?model_id={model_id} to see supported language codes.",
        )

    if tgt_lang not in valid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language code for {model_id}: '{tgt_lang}'. "
            f"Use GET /languages?model_id={model_id} to see supported language codes.",
        )

    translated_text = backend.translate(request.text, src_lang, tgt_lang)

    return TranslateResponse(
        original_text=request.text,
        translated_text=translated_text,
        source_language_code=src_lang,
        target_language_code=tgt_lang,
        model_id=model_id,
    )

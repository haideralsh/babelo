"""Translation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.model import LANGUAGE_CODES, get_model_manager

router = APIRouter(prefix="/translate", tags=["translate"])


class TranslateRequest(BaseModel):
    """Request model for translation."""

    text: str
    source_language_code: str
    target_language_code: str


class TranslateResponse(BaseModel):
    """Response model for translation."""

    original_text: str
    translated_text: str
    source_language_code: str
    target_language_code: str


@router.post("", response_model=TranslateResponse)
async def translate(request: TranslateRequest) -> TranslateResponse:
    """Translate text between languages.

    Translates the provided text from the source language to the target language
    using the NLLB model. The model must be downloaded first using the
    /model/download endpoint.

    Args:
        request: The translation request containing the text and language settings.
            - text: The text to translate
            - source_language_code: Source language NLLB code (required, e.g., "eng_Latn")
            - target_language_code: Target language NLLB code (required, e.g., "fra_Latn")

    Returns:
        The translated text along with language information.

    Raises:
        HTTPException: If the model is not downloaded or language code is not supported.
    """
    manager = get_model_manager()

    if not manager.is_downloaded:
        raise HTTPException(
            status_code=400,
            detail="Model not downloaded. Please call POST /model/download first.",
        )

    valid_codes = set(LANGUAGE_CODES.values())

    src_lang = request.source_language_code
    tgt_lang = request.target_language_code

    if src_lang not in valid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source language code: '{src_lang}'. "
            f"Use GET /languages to see supported language codes.",
        )

    if tgt_lang not in valid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported target language code: '{tgt_lang}'. "
            f"Use GET /languages to see supported language codes.",
        )

    translated_text = manager.translate(request.text, src_lang, tgt_lang)

    return TranslateResponse(
        original_text=request.text,
        translated_text=translated_text,
        source_language_code=src_lang,
        target_language_code=tgt_lang,
    )


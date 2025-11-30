from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from core.model import LANGUAGE_CODES, MODEL_NAME, get_model_manager

app = FastAPI(
    title="Bab API",
    description="A FastAPI backend service",
    version="0.1.0",
)


class ModelStatusResponse(BaseModel):
    """Response model for model status."""

    model_name: str
    cache_dir: str
    model_path: str
    is_downloaded: bool
    is_loaded: bool


class ModelVerifyResponse(BaseModel):
    """Response model for model verification."""

    model_path: str
    all_files_present: bool
    files: dict[str, bool]


class ModelDownloadResponse(BaseModel):
    """Response model for model download."""

    success: bool
    message: str
    model_path: str


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


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Bab API"}


@app.get("/model/status", response_model=ModelStatusResponse)
async def model_status() -> ModelStatusResponse:
    """Show model status.

    Returns information about the model including whether it's downloaded
    and loaded in memory.
    """
    manager = get_model_manager()

    return ModelStatusResponse(
        model_name=MODEL_NAME,
        cache_dir=str(manager.cache_dir),
        model_path=str(manager.model_path),
        is_downloaded=manager.is_downloaded,
        is_loaded=manager.is_loaded,
    )


@app.get("/model/verify", response_model=ModelVerifyResponse)
async def model_verify() -> ModelVerifyResponse:
    """Verify model files are present.

    Checks if all required model files exist in the model directory.
    """
    manager = get_model_manager()

    if not manager.model_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Model directory does not exist. Run download first.",
        )

    results = manager.verify_model_files()
    all_present = all(results.values())

    return ModelVerifyResponse(
        model_path=str(manager.model_path),
        all_files_present=all_present,
        files=results,
    )


@app.post("/model/download", response_model=ModelDownloadResponse)
async def model_download(
    force: bool = Query(
        default=False,
        description="Force re-download even if model exists",
    ),
) -> ModelDownloadResponse:
    """Download the NLLB model.

    Downloads the model to the local cache directory. If the model is already
    downloaded, returns success unless force=True is specified.

    Args:
        force: If True, re-download even if model already exists.
    """
    manager = get_model_manager()

    if manager.is_downloaded and not force:
        return ModelDownloadResponse(
            success=True,
            message="Model already downloaded. Use force=true to re-download.",
            model_path=str(manager.model_path),
        )

    try:
        manager.download_model(force=force)
        return ModelDownloadResponse(
            success=True,
            message="Model downloaded successfully.",
            model_path=str(manager.model_path),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {e}",
        ) from e


@app.get("/languages")
async def list_languages() -> dict[str, list[str] | dict[str, str]]:
    """List all supported languages.

    Returns a list of language codes and a mapping of language names to their NLLB codes.
    """

    return {
        "language_codes": sorted(LANGUAGE_CODES.values()),
        "name_to_code": LANGUAGE_CODES,
    }


@app.post("/translate", response_model=TranslateResponse)
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

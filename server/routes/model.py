"""Model API routes."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.model import MODEL_NAME, get_model_manager

router = APIRouter(prefix="/model", tags=["model"])


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


class ModelRemoveResponse(BaseModel):
    """Response model for model removal."""

    success: bool
    message: str
    model_path: str


@router.get("/status", response_model=ModelStatusResponse)
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


@router.get("/verify", response_model=ModelVerifyResponse)
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


@router.post("/download", response_model=ModelDownloadResponse)
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


@router.post("/remove", response_model=ModelRemoveResponse)
async def model_remove() -> ModelRemoveResponse:
    """Remove the downloaded model from disk.

    Unloads the model from memory and deletes the model files from the cache
    directory. This operation is idempotent - if the model is not downloaded,
    returns success.
    """
    manager = get_model_manager()
    model_path = str(manager.model_path)

    if not manager.is_downloaded:
        return ModelRemoveResponse(
            success=True,
            message="Model not downloaded, nothing to remove.",
            model_path=model_path,
        )

    try:
        manager.delete_model()
        return ModelRemoveResponse(
            success=True,
            message="Model removed successfully.",
            model_path=model_path,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Removal failed: {e}",
        ) from e

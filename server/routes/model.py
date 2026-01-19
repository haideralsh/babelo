"""Model API routes."""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from core.model import (
    DEFAULT_MODEL_ID,
    MODEL_REGISTRY,
    get_available_models,
    get_model_info,
    get_model_manager,
)

router = APIRouter(prefix="/model", tags=["model"])


class ModelInfoResponse(BaseModel):
    """Response model for model info."""

    model_id: str
    repo_id: str
    display_name: str
    description: str
    model_type: str
    size_estimate: str
    requires_auth: bool


class ModelStatusResponse(BaseModel):
    """Response model for model status."""

    model_id: str
    model_name: str
    cache_dir: str
    model_path: str
    is_downloaded: bool
    is_loaded: bool


class ModelVerifyResponse(BaseModel):
    """Response model for model verification."""

    model_id: str
    model_path: str
    all_files_present: bool
    files: dict[str, bool]


class ModelDownloadResponse(BaseModel):
    """Response model for model download."""

    success: bool
    message: str
    model_id: str
    model_path: str


class ModelRemoveResponse(BaseModel):
    """Response model for model removal."""

    success: bool
    message: str
    model_id: str
    model_path: str


class ModelsListResponse(BaseModel):
    """Response model for listing all available models."""

    models: list[ModelInfoResponse]
    default_model_id: str


class ModelsStatusResponse(BaseModel):
    """Response model for status of all models."""

    models: list[ModelStatusResponse]


@router.get("/list", response_model=ModelsListResponse)
async def list_models() -> ModelsListResponse:
    """List all available translation models.

    Returns information about each supported model including its ID,
    display name, description, and whether it requires authentication.
    """
    models = get_available_models()

    return ModelsListResponse(
        models=[
            ModelInfoResponse(
                model_id=m.model_id,
                repo_id=m.repo_id,
                display_name=m.display_name,
                description=m.description,
                model_type=m.model_type,
                size_estimate=m.size_estimate,
                requires_auth=m.requires_auth,
            )
            for m in models
        ],
        default_model_id=DEFAULT_MODEL_ID,
    )


@router.get("/list/status", response_model=ModelsStatusResponse)
async def list_models_status() -> ModelsStatusResponse:
    """Get download and load status for all available models."""
    manager = get_model_manager()
    models = []

    for model_id in MODEL_REGISTRY:
        backend = manager.get_backend(model_id)
        info = get_model_info(model_id)
        models.append(
            ModelStatusResponse(
                model_id=model_id,
                model_name=info.repo_id,
                cache_dir=str(manager.cache_dir),
                model_path=str(backend.model_path),
                is_downloaded=backend.is_downloaded,
                is_loaded=backend.is_loaded,
            )
        )

    return ModelsStatusResponse(models=models)


@router.get("/status", response_model=ModelStatusResponse)
async def model_status(
    model_id: str = Query(
        default=DEFAULT_MODEL_ID,
        description="Model ID to check status for",
    ),
) -> ModelStatusResponse:
    """Show model status.

    Returns information about the model including whether it's downloaded
    and loaded in memory.

    Args:
        model_id: The model to check. Defaults to 'nllb'.
    """
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    backend = manager.get_backend(model_id)
    info = get_model_info(model_id)

    return ModelStatusResponse(
        model_id=model_id,
        model_name=info.repo_id,
        cache_dir=str(manager.cache_dir),
        model_path=str(backend.model_path),
        is_downloaded=backend.is_downloaded,
        is_loaded=backend.is_loaded,
    )


@router.get("/verify", response_model=ModelVerifyResponse)
async def model_verify(
    model_id: str = Query(
        default=DEFAULT_MODEL_ID,
        description="Model ID to verify",
    ),
) -> ModelVerifyResponse:
    """Verify model files are present.

    Checks if all required model files exist in the model directory.

    Args:
        model_id: The model to verify. Defaults to 'nllb'.
    """
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    backend = manager.get_backend(model_id)

    if not backend.model_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Model directory does not exist. Run download first.",
        )

    results = backend.verify_model_files()
    all_present = all(results.values())

    return ModelVerifyResponse(
        model_id=model_id,
        model_path=str(backend.model_path),
        all_files_present=all_present,
        files=results,
    )


@router.post("/download", response_model=ModelDownloadResponse)
async def model_download(
    model_id: str = Query(
        default=DEFAULT_MODEL_ID,
        description="Model ID to download",
    ),
    force: bool = Query(
        default=False,
        description="Force re-download even if model exists",
    ),
) -> ModelDownloadResponse:
    """Download a translation model.

    Downloads the model to the local cache directory. If the model is already
    downloaded, returns success unless force=True is specified.

    Args:
        model_id: The model to download. Defaults to 'nllb'.
        force: If True, re-download even if model already exists.
    """
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    backend = manager.get_backend(model_id)

    if backend.is_downloaded and not force:
        return ModelDownloadResponse(
            success=True,
            message="Model already downloaded. Use force=true to re-download.",
            model_id=model_id,
            model_path=str(backend.model_path),
        )

    try:
        backend.download_model(force=force)
        return ModelDownloadResponse(
            success=True,
            message="Model downloaded successfully.",
            model_id=model_id,
            model_path=str(backend.model_path),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Download failed: {e}",
        ) from e


@router.post("/remove", response_model=ModelRemoveResponse)
async def model_remove(
    model_id: str = Query(
        default=DEFAULT_MODEL_ID,
        description="Model ID to remove",
    ),
) -> ModelRemoveResponse:
    """Remove the downloaded model from disk.

    Unloads the model from memory and deletes the model files from the cache
    directory. This operation is idempotent - if the model is not downloaded,
    returns success.

    Args:
        model_id: The model to remove. Defaults to 'nllb'.
    """
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}",
        )

    manager = get_model_manager()
    backend = manager.get_backend(model_id)
    model_path = str(backend.model_path)

    if not backend.is_downloaded:
        return ModelRemoveResponse(
            success=True,
            message="Model not downloaded, nothing to remove.",
            model_id=model_id,
            model_path=model_path,
        )

    try:
        backend.delete_model()
        return ModelRemoveResponse(
            success=True,
            message="Model removed successfully.",
            model_id=model_id,
            model_path=model_path,
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Removal failed: {e}",
        ) from e

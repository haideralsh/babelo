"""Model management module for translation models.

This module handles:
- Multi-model registry supporting NLLB and TranslateGemma
- Downloading models to a local cache
- Loading models and tokenizers/processors
- Keeping them in memory for reuse
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from huggingface_hub import snapshot_download

from core.languages import (
    NLLB_LANGUAGE_CODES,
    get_language_codes,
)

if TYPE_CHECKING:
    from transformers import (
        AutoModelForImageTextToText,
        AutoModelForSeq2SeqLM,
        AutoProcessor,
        AutoTokenizer,
    )

logger = logging.getLogger(__name__)

# Default cache directory for all models
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "bab" / "models"

# Re-export for backward compatibility
LANGUAGE_CODES = NLLB_LANGUAGE_CODES
MODEL_NAME = "facebook/nllb-200-distilled-600M"


class ModelInfo:
    """Metadata about a translation model."""

    def __init__(
        self,
        model_id: str,
        repo_id: str,
        display_name: str,
        description: str,
        model_type: str,
        size_estimate: str,
        requires_auth: bool = False,
    ):
        self.model_id = model_id
        self.repo_id = repo_id
        self.display_name = display_name
        self.description = description
        self.model_type = model_type  # 'seq2seq' or 'image_text_to_text'
        self.size_estimate = size_estimate
        self.requires_auth = requires_auth

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "model_id": self.model_id,
            "repo_id": self.repo_id,
            "display_name": self.display_name,
            "description": self.description,
            "model_type": self.model_type,
            "size_estimate": self.size_estimate,
            "requires_auth": self.requires_auth,
        }


# Model registry with metadata
MODEL_REGISTRY: dict[str, ModelInfo] = {
    "nllb": ModelInfo(
        model_id="nllb",
        repo_id="facebook/nllb-200-distilled-600M",
        display_name="NLLB-200",
        description="Meta's No Language Left Behind model supporting 200+ languages",
        model_type="seq2seq",
        size_estimate="~2.5GB",
        requires_auth=False,
    ),
    "translategemma": ModelInfo(
        model_id="translategemma",
        repo_id="google/translategemma-4b-it",
        display_name="TranslateGemma",
        description="Google's lightweight translation model based on Gemma 3",
        model_type="image_text_to_text",
        size_estimate="~8GB",
        requires_auth=True,  # Requires HF license acceptance
    ),
}

DEFAULT_MODEL_ID = "nllb"


def get_available_models() -> list[ModelInfo]:
    """Get list of all available models."""
    return list(MODEL_REGISTRY.values())


def get_model_info(model_id: str) -> ModelInfo:
    """Get metadata for a specific model.

    Args:
        model_id: The model identifier.

    Returns:
        ModelInfo for the requested model.

    Raises:
        ValueError: If model_id is not recognized.
    """
    if model_id not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model_id: {model_id}. "
            f"Available models: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[model_id]


class TranslationBackend(ABC):
    """Abstract base class for translation model backends."""

    def __init__(self, model_info: ModelInfo, cache_dir: Path):
        self._model_info = model_info
        self._cache_dir = cache_dir
        self._is_loaded = False

    @property
    def model_info(self) -> ModelInfo:
        """Get model metadata."""
        return self._model_info

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory path."""
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, path: Path | str) -> None:
        """Set the cache directory path."""
        self._cache_dir = Path(path)

    @property
    def model_path(self) -> Path:
        """Get the full path to the model directory."""
        return self._cache_dir / self._model_info.repo_id.replace("/", "--")

    @property
    def is_loaded(self) -> bool:
        """Check if the model is currently loaded in memory."""
        return self._is_loaded

    @property
    def is_downloaded(self) -> bool:
        """Check if the model files exist locally."""
        if not self.model_path.exists():
            return False
        # Check for essential files
        required_files = ["config.json"]
        return all((self.model_path / f).exists() for f in required_files)

    def download_model(self, force: bool = False) -> Path:
        """Download the model to the local cache.

        Args:
            force: If True, re-download even if files exist.

        Returns:
            Path to the downloaded model directory.

        Raises:
            RuntimeError: If download fails.
        """
        if self.is_downloaded and not force:
            logger.info(f"Model already downloaded at {self.model_path}")
            return self.model_path

        logger.info(
            f"Downloading model {self._model_info.repo_id} to {self._cache_dir}"
        )

        try:
            # Ensure cache directory exists
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Download model snapshot
            downloaded_path = snapshot_download(
                repo_id=self._model_info.repo_id,
                local_dir=self.model_path,
                local_dir_use_symlinks=False,
            )

            logger.info(f"Model downloaded successfully to {downloaded_path}")
            return Path(downloaded_path)

        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "403" in error_msg:
                raise RuntimeError(
                    f"Access denied for {self._model_info.repo_id}. "
                    "This model requires accepting the license on Hugging Face "
                    "and setting HF_TOKEN environment variable. "
                    f"Visit: https://huggingface.co/{self._model_info.repo_id}"
                ) from e
            logger.error(f"Failed to download model: {e}")
            raise RuntimeError(
                f"Failed to download model {self._model_info.repo_id}: {e}"
            ) from e

    def delete_model(self) -> bool:
        """Delete the downloaded model from disk.

        Returns:
            True if deletion was successful or model didn't exist.
        """
        import shutil

        self.unload_model()

        if not self.model_path.exists():
            logger.info("Model not downloaded, nothing to delete")
            return True

        try:
            shutil.rmtree(self.model_path)
            logger.info(f"Model deleted from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            raise RuntimeError(
                f"Failed to delete model at {self.model_path}: {e}"
            ) from e

    @abstractmethod
    def load_model(self) -> Any:
        """Load the model into memory."""
        pass

    @abstractmethod
    def unload_model(self) -> None:
        """Unload the model from memory."""
        pass

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages."""
        pass

    @abstractmethod
    def verify_model_files(self) -> dict[str, bool]:
        """Verify that all necessary model files are present."""
        pass

    def get_language_codes(self) -> dict[str, str]:
        """Get the language codes supported by this model."""
        return get_language_codes(self._model_info.model_id)


class NLLBBackend(TranslationBackend):
    """Backend for Meta's NLLB-200 translation model."""

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR):
        super().__init__(MODEL_REGISTRY["nllb"], cache_dir)
        self._model: AutoModelForSeq2SeqLM | None = None
        self._tokenizer: AutoTokenizer | None = None

    def load_model(self) -> tuple["AutoModelForSeq2SeqLM", "AutoTokenizer"]:
        """Load the model and tokenizer into memory."""
        if self._is_loaded and self._model is not None and self._tokenizer is not None:
            logger.debug("Returning cached model and tokenizer")
            return self._model, self._tokenizer

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        if not self.is_downloaded:
            logger.info("Model not found locally, downloading...")
            self.download_model()

        logger.info(f"Loading model from {self.model_path}")

        try:
            tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            logger.info("Tokenizer loaded successfully")

            model: AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            logger.info("Model loaded successfully")

            self._model = model
            self._tokenizer = tokenizer
            self._is_loaded = True

            return model, tokenizer

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model = None
            self._tokenizer = None
            self._is_loaded = False
            raise RuntimeError(
                f"Failed to load model from {self.model_path}: {e}"
            ) from e

    def unload_model(self) -> None:
        """Unload the model from memory to free resources."""
        if self._model is not None:
            del self._model
            self._model = None

        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None

        self._is_loaded = False
        logger.info("Model unloaded from memory")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages using NLLB codes."""
        model, tokenizer = self.load_model()
        tokenizer.src_lang = source_lang
        inputs = tokenizer(text, return_tensors="pt")
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_lang),
            max_length=512,
        )
        return tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]

    def verify_model_files(self) -> dict[str, bool]:
        """Verify that all necessary model files are present."""
        required_files = [
            "config.json",
            "generation_config.json",
            "sentencepiece.bpe.model",
            "special_tokens_map.json",
            "tokenizer_config.json",
            "tokenizer.json",
        ]

        results = {}
        for filename in required_files:
            file_path = self.model_path / filename
            results[filename] = file_path.exists()

        # Check for model weights (either safetensors or pytorch format)
        has_safetensors = (self.model_path / "model.safetensors").exists()
        has_pytorch = (self.model_path / "pytorch_model.bin").exists()
        results["model weights (safetensors or pytorch)"] = (
            has_safetensors or has_pytorch
        )

        return results

    def get_model(self) -> "AutoModelForSeq2SeqLM":
        """Get the loaded model, loading it if necessary."""
        if not self._is_loaded or self._model is None:
            self.load_model()
        return self._model  # type: ignore[return-value]

    def get_tokenizer(self) -> "AutoTokenizer":
        """Get the loaded tokenizer, loading it if necessary."""
        if not self._is_loaded or self._tokenizer is None:
            self.load_model()
        return self._tokenizer  # type: ignore[return-value]


class TranslateGemmaBackend(TranslationBackend):
    """Backend for Google's TranslateGemma model."""

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR):
        super().__init__(MODEL_REGISTRY["translategemma"], cache_dir)
        self._model: AutoModelForImageTextToText | None = None
        self._processor: AutoProcessor | None = None

    def load_model(self) -> tuple["AutoModelForImageTextToText", "AutoProcessor"]:
        """Load the model and processor into memory."""
        if self._is_loaded and self._model is not None and self._processor is not None:
            logger.debug("Returning cached model and processor")
            return self._model, self._processor

        from transformers import AutoModelForImageTextToText, AutoProcessor

        if not self.is_downloaded:
            logger.info("Model not found locally, downloading...")
            self.download_model()

        logger.info(f"Loading model from {self.model_path}")

        try:
            processor: AutoProcessor = AutoProcessor.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            logger.info("Processor loaded successfully")

            import torch

            model: AutoModelForImageTextToText = (
                AutoModelForImageTextToText.from_pretrained(
                    self.model_path,
                    local_files_only=True,
                    device_map="auto",
                    torch_dtype=torch.bfloat16,
                )
            )
            logger.info("Model loaded successfully")

            self._model = model
            self._processor = processor
            self._is_loaded = True

            return model, processor

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model = None
            self._processor = None
            self._is_loaded = False
            raise RuntimeError(
                f"Failed to load model from {self.model_path}: {e}"
            ) from e

    def unload_model(self) -> None:
        """Unload the model from memory to free resources."""
        if self._model is not None:
            del self._model
            self._model = None

        if self._processor is not None:
            del self._processor
            self._processor = None

        self._is_loaded = False
        logger.info("Model unloaded from memory")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text using TranslateGemma's chat template.

        Args:
            text: The text to translate.
            source_lang: Source language ISO code (e.g., "en", "de-DE").
            target_lang: Target language ISO code (e.g., "fr", "es-ES").

        Returns:
            The translated text.
        """
        import torch

        model, processor = self.load_model()

        # Build the chat message using TranslateGemma's template
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "source_lang_code": source_lang,
                        "target_lang_code": target_lang,
                        "text": text,
                    }
                ],
            }
        ]

        # Apply the chat template
        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(model.device, dtype=torch.bfloat16)

        input_len = len(inputs["input_ids"][0])

        with torch.inference_mode():
            generation = model.generate(**inputs, do_sample=False, max_new_tokens=512)

        generation = generation[0][input_len:]
        decoded = processor.decode(generation, skip_special_tokens=True)

        return decoded

    def verify_model_files(self) -> dict[str, bool]:
        """Verify that all necessary model files are present."""
        required_files = [
            "config.json",
            "generation_config.json",
            "preprocessor_config.json",
            "tokenizer_config.json",
            "tokenizer.json",
        ]

        results = {}
        for filename in required_files:
            file_path = self.model_path / filename
            results[filename] = file_path.exists()

        # Check for model weights (safetensors shards)
        has_safetensors = any(
            f.name.endswith(".safetensors")
            for f in self.model_path.glob("*.safetensors")
        )
        results["model weights (safetensors)"] = has_safetensors

        return results

    def get_model(self) -> "AutoModelForImageTextToText":
        """Get the loaded model, loading it if necessary."""
        if not self._is_loaded or self._model is None:
            self.load_model()
        return self._model  # type: ignore[return-value]

    def get_processor(self) -> "AutoProcessor":
        """Get the loaded processor, loading it if necessary."""
        if not self._is_loaded or self._processor is None:
            self.load_model()
        return self._processor  # type: ignore[return-value]


class ModelManager:
    """Manages multiple translation model backends.

    This class provides a unified interface for managing different translation
    models with singleton-like behavior per model_id.
    """

    _instance: "ModelManager | None" = None
    _backends: dict[str, TranslationBackend] = {}

    def __new__(cls) -> "ModelManager":
        """Ensure only one instance of ModelManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._backends = {}
        return cls._instance

    def __init__(self) -> None:
        """Initialize the ModelManager."""
        self._cache_dir = DEFAULT_CACHE_DIR
        # For backward compatibility, default to NLLB
        self._current_model_id = DEFAULT_MODEL_ID

    @property
    def cache_dir(self) -> Path:
        """Get the cache directory path."""
        return self._cache_dir

    @cache_dir.setter
    def cache_dir(self, path: Path | str) -> None:
        """Set the cache directory path."""
        self._cache_dir = Path(path)
        # Update cache dir for all loaded backends
        for backend in self._backends.values():
            backend.cache_dir = self._cache_dir

    def get_backend(self, model_id: str | None = None) -> TranslationBackend:
        """Get or create a backend for the specified model.

        Args:
            model_id: The model identifier. Defaults to 'nllb'.

        Returns:
            The translation backend for the model.
        """
        model_id = model_id or self._current_model_id

        if model_id not in self._backends:
            if model_id == "nllb":
                self._backends[model_id] = NLLBBackend(self._cache_dir)
            elif model_id == "translategemma":
                self._backends[model_id] = TranslateGemmaBackend(self._cache_dir)
            else:
                raise ValueError(
                    f"Unknown model_id: {model_id}. "
                    f"Available models: {list(MODEL_REGISTRY.keys())}"
                )

        return self._backends[model_id]

    # Backward compatibility properties (delegate to NLLB backend)
    @property
    def model_path(self) -> Path:
        """Get the full path to the default model directory."""
        return self.get_backend().model_path

    @property
    def is_loaded(self) -> bool:
        """Check if the default model is currently loaded in memory."""
        return self.get_backend().is_loaded

    @property
    def is_downloaded(self) -> bool:
        """Check if the default model files exist locally."""
        return self.get_backend().is_downloaded

    def download_model(self, force: bool = False, model_id: str | None = None) -> Path:
        """Download a model to the local cache."""
        return self.get_backend(model_id).download_model(force=force)

    def load_model(self, model_id: str | None = None) -> Any:
        """Load a model into memory."""
        return self.get_backend(model_id).load_model()

    def unload_model(self, model_id: str | None = None) -> None:
        """Unload a model from memory."""
        self.get_backend(model_id).unload_model()

    def delete_model(self, model_id: str | None = None) -> bool:
        """Delete a downloaded model from disk."""
        return self.get_backend(model_id).delete_model()

    def verify_model_files(self, model_id: str | None = None) -> dict[str, bool]:
        """Verify that all necessary model files are present."""
        return self.get_backend(model_id).verify_model_files()

    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model_id: str | None = None,
    ) -> str:
        """Translate text between languages using the specified model."""
        return self.get_backend(model_id).translate(text, source_lang, target_lang)

    def get_language_codes(self, model_id: str | None = None) -> dict[str, str]:
        """Get the language codes for a specific model."""
        return self.get_backend(model_id).get_language_codes()

    # Backward compatibility methods for NLLB
    def get_model(self) -> "AutoModelForSeq2SeqLM":
        """Get the loaded NLLB model."""
        backend = self.get_backend("nllb")
        if isinstance(backend, NLLBBackend):
            return backend.get_model()
        raise TypeError("get_model() only supported for NLLB backend")

    def get_tokenizer(self) -> "AutoTokenizer":
        """Get the loaded NLLB tokenizer."""
        backend = self.get_backend("nllb")
        if isinstance(backend, NLLBBackend):
            return backend.get_tokenizer()
        raise TypeError("get_tokenizer() only supported for NLLB backend")


# Global model manager instance
_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    """Get the global ModelManager instance.

    Returns:
        The global ModelManager singleton.
    """
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager

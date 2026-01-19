"""Tests for the model management module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.model import (
    DEFAULT_MODEL_ID,
    MODEL_REGISTRY,
    ModelManager,
    NLLBBackend,
    TranslateGemmaBackend,
    get_available_models,
    get_model_info,
    get_model_manager,
)
from core.languages import (
    NLLB_LANGUAGE_CODES,
    TRANSLATEGEMMA_LANGUAGE_CODES,
    get_language_codes,
)


class TestModelRegistry:
    """Tests for the model registry."""

    def test_default_model_id(self):
        """Test that default model ID is 'nllb'."""
        assert DEFAULT_MODEL_ID == "nllb"

    def test_model_registry_contains_expected_models(self):
        """Test that registry contains both NLLB and TranslateGemma."""
        assert "nllb" in MODEL_REGISTRY
        assert "translategemma" in MODEL_REGISTRY

    def test_get_available_models(self):
        """Test that get_available_models returns all models."""
        models = get_available_models()
        assert len(models) == 2
        model_ids = [m.model_id for m in models]
        assert "nllb" in model_ids
        assert "translategemma" in model_ids

    def test_get_model_info_nllb(self):
        """Test getting model info for NLLB."""
        info = get_model_info("nllb")
        assert info.model_id == "nllb"
        assert info.repo_id == "facebook/nllb-200-distilled-600M"
        assert info.requires_auth is False

    def test_get_model_info_translategemma(self):
        """Test getting model info for TranslateGemma."""
        info = get_model_info("translategemma")
        assert info.model_id == "translategemma"
        assert info.repo_id == "google/translategemma-4b-it"
        assert info.requires_auth is True

    def test_get_model_info_unknown(self):
        """Test that unknown model_id raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model_id"):
            get_model_info("unknown_model")


class TestLanguageCodes:
    """Tests for language code mappings."""

    def test_nllb_language_codes_not_empty(self):
        """Test that NLLB language codes are populated."""
        assert len(NLLB_LANGUAGE_CODES) > 0
        assert "English" in NLLB_LANGUAGE_CODES
        assert NLLB_LANGUAGE_CODES["English"] == "eng_Latn"

    def test_translategemma_language_codes_not_empty(self):
        """Test that TranslateGemma language codes are populated."""
        assert len(TRANSLATEGEMMA_LANGUAGE_CODES) > 0
        assert "English" in TRANSLATEGEMMA_LANGUAGE_CODES
        assert TRANSLATEGEMMA_LANGUAGE_CODES["English"] == "en"

    def test_get_language_codes_nllb(self):
        """Test getting language codes for NLLB."""
        codes = get_language_codes("nllb")
        assert codes == NLLB_LANGUAGE_CODES

    def test_get_language_codes_translategemma(self):
        """Test getting language codes for TranslateGemma."""
        codes = get_language_codes("translategemma")
        assert codes == TRANSLATEGEMMA_LANGUAGE_CODES

    def test_get_language_codes_unknown(self):
        """Test that unknown model_id raises ValueError."""
        with pytest.raises(ValueError, match="Unknown model_id"):
            get_language_codes("unknown")


class TestModelManager:
    """Tests for the ModelManager class."""

    def test_singleton_pattern(self):
        """Test that ModelManager implements singleton pattern."""
        manager1 = ModelManager()
        manager2 = ModelManager()
        assert manager1 is manager2

    def test_default_cache_dir(self):
        """Test that default cache directory is set correctly."""
        manager = ModelManager()
        expected = Path.home() / ".cache" / "bab" / "models"
        assert manager.cache_dir == expected

    def test_custom_cache_dir(self):
        """Test setting a custom cache directory."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            custom_path = Path("/tmp/custom_cache")
            manager.cache_dir = custom_path
            assert manager.cache_dir == custom_path

            # Test with string path
            manager.cache_dir = "/tmp/another_cache"
            assert manager.cache_dir == Path("/tmp/another_cache")
        finally:
            # Restore original
            manager.cache_dir = original_cache_dir

    def test_get_backend_nllb(self):
        """Test getting NLLB backend."""
        manager = ModelManager()
        backend = manager.get_backend("nllb")
        assert isinstance(backend, NLLBBackend)

    def test_get_backend_translategemma(self):
        """Test getting TranslateGemma backend."""
        manager = ModelManager()
        backend = manager.get_backend("translategemma")
        assert isinstance(backend, TranslateGemmaBackend)

    def test_get_backend_default(self):
        """Test that default backend is NLLB."""
        manager = ModelManager()
        backend = manager.get_backend()
        assert isinstance(backend, NLLBBackend)

    def test_get_backend_unknown(self):
        """Test that unknown model_id raises ValueError."""
        manager = ModelManager()
        with pytest.raises(ValueError, match="Unknown model_id"):
            manager.get_backend("unknown")

    def test_get_language_codes_via_manager(self):
        """Test getting language codes through the manager."""
        manager = ModelManager()
        nllb_codes = manager.get_language_codes("nllb")
        assert nllb_codes == NLLB_LANGUAGE_CODES

        gemma_codes = manager.get_language_codes("translategemma")
        assert gemma_codes == TRANSLATEGEMMA_LANGUAGE_CODES


class TestNLLBBackend:
    """Tests for the NLLBBackend class."""

    def test_model_path(self):
        """Test that model path is constructed correctly."""
        backend = NLLBBackend()
        expected_model_dir = "facebook--nllb-200-distilled-600M"
        assert backend.model_path.name == expected_model_dir

    def test_is_downloaded_false_when_no_directory(self):
        """Test is_downloaded returns False when directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            assert backend.is_downloaded is False

    def test_is_downloaded_false_when_missing_files(self):
        """Test is_downloaded returns False when required files are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            # Create model directory but without required files
            backend.model_path.mkdir(parents=True, exist_ok=True)
            assert backend.is_downloaded is False

    def test_is_downloaded_true_when_files_present(self):
        """Test is_downloaded returns True when required files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            # Create model directory with required files
            backend.model_path.mkdir(parents=True, exist_ok=True)
            (backend.model_path / "config.json").touch()
            assert backend.is_downloaded is True

    def test_is_loaded_initially_false(self):
        """Test that is_loaded is initially False."""
        backend = NLLBBackend()
        # Ensure fresh state
        backend._is_loaded = False
        backend._model = None
        backend._tokenizer = None
        assert backend.is_loaded is False

    def test_verify_model_files(self):
        """Test verify_model_files returns correct status for each file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            backend.model_path.mkdir(parents=True, exist_ok=True)

            # Create some files but not all
            (backend.model_path / "config.json").touch()
            (backend.model_path / "tokenizer_config.json").touch()

            results = backend.verify_model_files()

            assert results["config.json"] is True
            assert results["tokenizer_config.json"] is True
            assert results["sentencepiece.bpe.model"] is False

    @patch("core.model.snapshot_download")
    def test_download_model_skips_if_already_downloaded(self, mock_download):
        """Test that download is skipped if model already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            # Create model directory with required files
            backend.model_path.mkdir(parents=True, exist_ok=True)
            (backend.model_path / "config.json").touch()

            result = backend.download_model()

            assert result == backend.model_path
            mock_download.assert_not_called()

    @patch("core.model.snapshot_download")
    def test_download_model_calls_snapshot_download(self, mock_download):
        """Test that download calls snapshot_download correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            mock_download.return_value = str(backend.model_path)

            backend.download_model()

            mock_download.assert_called_once_with(
                repo_id="facebook/nllb-200-distilled-600M",
                local_dir=backend.model_path,
                local_dir_use_symlinks=False,
            )

    @patch("core.model.snapshot_download")
    def test_download_model_force_redownload(self, mock_download):
        """Test that force=True triggers re-download."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            # Create model directory with required files
            backend.model_path.mkdir(parents=True, exist_ok=True)
            (backend.model_path / "config.json").touch()

            mock_download.return_value = str(backend.model_path)

            backend.download_model(force=True)

            mock_download.assert_called_once()

    @patch("core.model.snapshot_download")
    def test_download_model_raises_on_failure(self, mock_download):
        """Test that download raises RuntimeError on failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = NLLBBackend(cache_dir=Path(tmpdir))
            mock_download.side_effect = Exception("Network error")

            with pytest.raises(RuntimeError, match="Failed to download model"):
                backend.download_model()

    def test_unload_model(self):
        """Test unloading model from memory."""
        backend = NLLBBackend()

        # Simulate loaded state
        backend._model = MagicMock()
        backend._tokenizer = MagicMock()
        backend._is_loaded = True

        backend.unload_model()

        assert backend._model is None
        assert backend._tokenizer is None
        assert backend._is_loaded is False

    def test_get_language_codes(self):
        """Test getting language codes from backend."""
        backend = NLLBBackend()
        codes = backend.get_language_codes()
        assert codes == NLLB_LANGUAGE_CODES


class TestTranslateGemmaBackend:
    """Tests for the TranslateGemmaBackend class."""

    def test_model_path(self):
        """Test that model path is constructed correctly."""
        backend = TranslateGemmaBackend()
        expected_model_dir = "google--translategemma-4b-it"
        assert backend.model_path.name == expected_model_dir

    def test_is_downloaded_false_when_no_directory(self):
        """Test is_downloaded returns False when directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = TranslateGemmaBackend(cache_dir=Path(tmpdir))
            assert backend.is_downloaded is False

    def test_requires_auth(self):
        """Test that TranslateGemma requires authentication."""
        backend = TranslateGemmaBackend()
        assert backend.model_info.requires_auth is True

    def test_get_language_codes(self):
        """Test getting language codes from backend."""
        backend = TranslateGemmaBackend()
        codes = backend.get_language_codes()
        assert codes == TRANSLATEGEMMA_LANGUAGE_CODES

    @patch("core.model.snapshot_download")
    def test_download_model_auth_error(self, mock_download):
        """Test that auth error is handled with helpful message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = TranslateGemmaBackend(cache_dir=Path(tmpdir))
            mock_download.side_effect = Exception("401 Unauthorized")

            with pytest.raises(RuntimeError, match="Access denied"):
                backend.download_model()


class TestGetModelManager:
    """Tests for the get_model_manager function."""

    def test_returns_model_manager(self):
        """Test that get_model_manager returns a ModelManager instance."""
        manager = get_model_manager()
        assert isinstance(manager, ModelManager)

    def test_returns_same_instance(self):
        """Test that get_model_manager returns the same instance."""
        manager1 = get_model_manager()
        manager2 = get_model_manager()
        assert manager1 is manager2


class TestModelLoading:
    """Tests for model loading functionality.

    These tests mock the transformers library to avoid loading the actual model.
    """

    def test_load_model_returns_cached_if_loaded(self):
        """Test that load_model returns cached instances if already loaded."""
        backend = NLLBBackend()

        # Simulate already loaded state
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        backend._model = mock_model
        backend._tokenizer = mock_tokenizer
        backend._is_loaded = True

        try:
            model, tokenizer = backend.load_model()

            assert model is mock_model
            assert tokenizer is mock_tokenizer
        finally:
            backend._is_loaded = False
            backend._model = None
            backend._tokenizer = None

    def test_get_model_returns_model(self):
        """Test that get_model returns the model."""
        backend = NLLBBackend()

        mock_model = MagicMock()
        backend._model = mock_model
        backend._tokenizer = MagicMock()
        backend._is_loaded = True

        try:
            result = backend.get_model()
            assert result is mock_model
        finally:
            backend._is_loaded = False
            backend._model = None
            backend._tokenizer = None

    def test_get_tokenizer_returns_tokenizer(self):
        """Test that get_tokenizer returns the tokenizer."""
        backend = NLLBBackend()

        mock_tokenizer = MagicMock()
        backend._model = MagicMock()
        backend._tokenizer = mock_tokenizer
        backend._is_loaded = True

        try:
            result = backend.get_tokenizer()
            assert result is mock_tokenizer
        finally:
            backend._is_loaded = False
            backend._model = None
            backend._tokenizer = None

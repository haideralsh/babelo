"""Tests for the model management module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bab.model import MODEL_NAME, ModelManager, get_model_manager


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

    def test_model_path(self):
        """Test that model path is constructed correctly."""
        manager = ModelManager()
        expected_model_dir = MODEL_NAME.replace("/", "--")
        assert manager.model_path.name == expected_model_dir
        assert manager.model_path.parent == manager.cache_dir

    def test_is_downloaded_false_when_no_directory(self):
        """Test is_downloaded returns False when directory doesn't exist."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            manager.cache_dir = Path("/nonexistent/path/that/doesnt/exist")
            assert manager.is_downloaded is False
        finally:
            manager.cache_dir = original_cache_dir

    def test_is_downloaded_false_when_missing_files(self):
        """Test is_downloaded returns False when required files are missing."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                # Create model directory but without required files
                manager.model_path.mkdir(parents=True, exist_ok=True)
                assert manager.is_downloaded is False
        finally:
            manager.cache_dir = original_cache_dir

    def test_is_downloaded_true_when_files_present(self):
        """Test is_downloaded returns True when required files exist."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                # Create model directory with required files
                manager.model_path.mkdir(parents=True, exist_ok=True)
                (manager.model_path / "config.json").touch()
                (manager.model_path / "tokenizer_config.json").touch()
                assert manager.is_downloaded is True
        finally:
            manager.cache_dir = original_cache_dir

    def test_is_loaded_initially_false(self):
        """Test that is_loaded is initially False."""
        # Reset the singleton state for this test
        ModelManager._is_loaded = False
        ModelManager._model = None
        ModelManager._tokenizer = None

        manager = ModelManager()
        assert manager.is_loaded is False

    def test_verify_model_files(self):
        """Test verify_model_files returns correct status for each file."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                manager.model_path.mkdir(parents=True, exist_ok=True)

                # Create some files but not all
                (manager.model_path / "config.json").touch()
                (manager.model_path / "tokenizer_config.json").touch()

                results = manager.verify_model_files()

                assert results["config.json"] is True
                assert results["tokenizer_config.json"] is True
                assert results["model.safetensors"] is False
                assert results["sentencepiece.bpe.model"] is False
        finally:
            manager.cache_dir = original_cache_dir

    @patch("bab.model.snapshot_download")
    def test_download_model_skips_if_already_downloaded(self, mock_download):
        """Test that download is skipped if model already exists."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                # Create model directory with required files
                manager.model_path.mkdir(parents=True, exist_ok=True)
                (manager.model_path / "config.json").touch()
                (manager.model_path / "tokenizer_config.json").touch()

                result = manager.download_model()

                assert result == manager.model_path
                mock_download.assert_not_called()
        finally:
            manager.cache_dir = original_cache_dir

    @patch("bab.model.snapshot_download")
    def test_download_model_calls_snapshot_download(self, mock_download):
        """Test that download calls snapshot_download correctly."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                mock_download.return_value = str(manager.model_path)

                manager.download_model()

                mock_download.assert_called_once_with(
                    repo_id=MODEL_NAME,
                    local_dir=manager.model_path,
                    local_dir_use_symlinks=False,
                )
        finally:
            manager.cache_dir = original_cache_dir

    @patch("bab.model.snapshot_download")
    def test_download_model_force_redownload(self, mock_download):
        """Test that force=True triggers re-download."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                # Create model directory with required files
                manager.model_path.mkdir(parents=True, exist_ok=True)
                (manager.model_path / "config.json").touch()
                (manager.model_path / "tokenizer_config.json").touch()

                mock_download.return_value = str(manager.model_path)

                manager.download_model(force=True)

                mock_download.assert_called_once()
        finally:
            manager.cache_dir = original_cache_dir

    @patch("bab.model.snapshot_download")
    def test_download_model_raises_on_failure(self, mock_download):
        """Test that download raises RuntimeError on failure."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir
                mock_download.side_effect = Exception("Network error")

                with pytest.raises(RuntimeError, match="Failed to download model"):
                    manager.download_model()
        finally:
            manager.cache_dir = original_cache_dir

    def test_unload_model(self):
        """Test unloading model from memory."""
        manager = ModelManager()

        # Simulate loaded state
        manager._model = MagicMock()
        manager._tokenizer = MagicMock()
        manager._is_loaded = True

        manager.unload_model()

        assert manager._model is None
        assert manager._tokenizer is None
        assert manager._is_loaded is False


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

    @patch("bab.model.ModelManager.download_model")
    def test_load_model_downloads_if_not_present(self, mock_download):
        """Test that load_model downloads model if not present."""
        manager = ModelManager()
        original_cache_dir = manager.cache_dir
        manager._is_loaded = False
        manager._model = None
        manager._tokenizer = None

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                manager.cache_dir = tmpdir

                # Mock the is_downloaded property to return False initially
                with patch.object(
                    ModelManager,
                    "is_downloaded",
                    new_callable=lambda: property(lambda self: False),
                ):
                    with patch(
                        "transformers.AutoModelForSeq2SeqLM.from_pretrained"
                    ) as mock_model:
                        with patch(
                            "transformers.AutoTokenizer.from_pretrained"
                        ) as mock_tokenizer:
                            mock_model.return_value = MagicMock()
                            mock_tokenizer.return_value = MagicMock()

                            try:
                                manager.load_model()
                            except Exception:
                                pass  # May fail due to mocking, but download should be called

                            mock_download.assert_called_once()
        finally:
            manager.cache_dir = original_cache_dir
            manager._is_loaded = False
            manager._model = None
            manager._tokenizer = None

    def test_load_model_returns_cached_if_loaded(self):
        """Test that load_model returns cached instances if already loaded."""
        manager = ModelManager()

        # Simulate already loaded state
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        manager._model = mock_model
        manager._tokenizer = mock_tokenizer
        manager._is_loaded = True

        try:
            model, tokenizer = manager.load_model()

            assert model is mock_model
            assert tokenizer is mock_tokenizer
        finally:
            manager._is_loaded = False
            manager._model = None
            manager._tokenizer = None

    def test_get_model_returns_model(self):
        """Test that get_model returns the model."""
        manager = ModelManager()

        mock_model = MagicMock()
        manager._model = mock_model
        manager._tokenizer = MagicMock()
        manager._is_loaded = True

        try:
            result = manager.get_model()
            assert result is mock_model
        finally:
            manager._is_loaded = False
            manager._model = None
            manager._tokenizer = None

    def test_get_tokenizer_returns_tokenizer(self):
        """Test that get_tokenizer returns the tokenizer."""
        manager = ModelManager()

        mock_tokenizer = MagicMock()
        manager._model = MagicMock()
        manager._tokenizer = mock_tokenizer
        manager._is_loaded = True

        try:
            result = manager.get_tokenizer()
            assert result is mock_tokenizer
        finally:
            manager._is_loaded = False
            manager._model = None
            manager._tokenizer = None

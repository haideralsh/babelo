"""Model management module for NLLB translation model.

This module handles:
- Downloading the NLLB model to a local cache
- Loading the model and tokenizer
- Keeping them in memory for reuse
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from huggingface_hub import snapshot_download

if TYPE_CHECKING:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "facebook/nllb-200-distilled-600M"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "bab" / "models"

LANGUAGE_CODES = {
    "Acehnese (Arabic script)": "ace_Arab",
    "Acehnese (Latin script)": "ace_Latn",
    "Mesopotamian Arabic": "acm_Arab",
    "Ta'izzi-Adeni Arabic": "acq_Arab",
    "Tunisian Arabic": "aeb_Arab",
    "Afrikaans": "afr_Latn",
    "South Levantine Arabic": "ajp_Arab",
    "Akan": "aka_Latn",
    "Amharic": "amh_Ethi",
    "North Levantine Arabic": "apc_Arab",
    "Modern Standard Arabic": "arb_Arab",
    "Modern Standard Arabic (Romanized)": "arb_Latn",
    "Najdi Arabic": "ars_Arab",
    "Moroccan Arabic": "ary_Arab",
    "Egyptian Arabic": "arz_Arab",
    "Assamese": "asm_Beng",
    "Asturian": "ast_Latn",
    "Awadhi": "awa_Deva",
    "Central Aymara": "ayr_Latn",
    "South Azerbaijani": "azb_Arab",
    "North Azerbaijani": "azj_Latn",
    "Bashkir": "bak_Cyrl",
    "Bambara": "bam_Latn",
    "Balinese": "ban_Latn",
    "Belarusian": "bel_Cyrl",
    "Bemba": "bem_Latn",
    "Bengali": "ben_Beng",
    "Bhojpuri": "bho_Deva",
    "Banjar (Arabic script)": "bjn_Arab",
    "Banjar (Latin script)": "bjn_Latn",
    "Standard Tibetan": "bod_Tibt",
    "Bosnian": "bos_Latn",
    "Buginese": "bug_Latn",
    "Bulgarian": "bul_Cyrl",
    "Catalan": "cat_Latn",
    "Cebuano": "ceb_Latn",
    "Czech": "ces_Latn",
    "Chokwe": "cjk_Latn",
    "Central Kurdish": "ckb_Arab",
    "Crimean Tatar": "crh_Latn",
    "Welsh": "cym_Latn",
    "Danish": "dan_Latn",
    "German": "deu_Latn",
    "Southwestern Dinka": "dik_Latn",
    "Dyula": "dyu_Latn",
    "Dzongkha": "dzo_Tibt",
    "Greek": "ell_Grek",
    "English": "eng_Latn",
    "Esperanto": "epo_Latn",
    "Estonian": "est_Latn",
    "Basque": "eus_Latn",
    "Ewe": "ewe_Latn",
    "Faroese": "fao_Latn",
    "Fijian": "fij_Latn",
    "Finnish": "fin_Latn",
    "Fon": "fon_Latn",
    "French": "fra_Latn",
    "Friulian": "fur_Latn",
    "Nigerian Fulfulde": "fuv_Latn",
    "Scottish Gaelic": "gla_Latn",
    "Irish": "gle_Latn",
    "Galician": "glg_Latn",
    "Guarani": "grn_Latn",
    "Gujarati": "guj_Gujr",
    "Haitian Creole": "hat_Latn",
    "Hausa": "hau_Latn",
    "Hebrew": "heb_Hebr",
    "Hindi": "hin_Deva",
    "Chhattisgarhi": "hne_Deva",
    "Croatian": "hrv_Latn",
    "Hungarian": "hun_Latn",
    "Armenian": "hye_Armn",
    "Igbo": "ibo_Latn",
    "Ilocano": "ilo_Latn",
    "Indonesian": "ind_Latn",
    "Icelandic": "isl_Latn",
    "Italian": "ita_Latn",
    "Javanese": "jav_Latn",
    "Japanese": "jpn_Jpan",
    "Kabyle": "kab_Latn",
    "Jingpho": "kac_Latn",
    "Kamba": "kam_Latn",
    "Kannada": "kan_Knda",
    "Kashmiri (Arabic script)": "kas_Arab",
    "Kashmiri (Devanagari script)": "kas_Deva",
    "Georgian": "kat_Geor",
    "Central Kanuri (Arabic script)": "knc_Arab",
    "Central Kanuri (Latin script)": "knc_Latn",
    "Kazakh": "kaz_Cyrl",
    "Kabiyè": "kbp_Latn",
    "Kabuverdianu": "kea_Latn",
    "Khmer": "khm_Khmr",
    "Kikuyu": "kik_Latn",
    "Kinyarwanda": "kin_Latn",
    "Kyrgyz": "kir_Cyrl",
    "Kimbundu": "kmb_Latn",
    "Northern Kurdish": "kmr_Latn",
    "Kikongo": "kon_Latn",
    "Korean": "kor_Hang",
    "Lao": "lao_Laoo",
    "Ligurian": "lij_Latn",
    "Limburgish": "lim_Latn",
    "Lingala": "lin_Latn",
    "Lithuanian": "lit_Latn",
    "Lombard": "lmo_Latn",
    "Latgalian": "ltg_Latn",
    "Luxembourgish": "ltz_Latn",
    "Luba-Kasai": "lua_Latn",
    "Ganda": "lug_Latn",
    "Luo": "luo_Latn",
    "Mizo": "lus_Latn",
    "Standard Latvian": "lvs_Latn",
    "Magahi": "mag_Deva",
    "Maithili": "mai_Deva",
    "Malayalam": "mal_Mlym",
    "Marathi": "mar_Deva",
    "Minangkabau (Arabic script)": "min_Arab",
    "Minangkabau (Latin script)": "min_Latn",
    "Macedonian": "mkd_Cyrl",
    "Plateau Malagasy": "plt_Latn",
    "Maltese": "mlt_Latn",
    "Meitei (Bengali script)": "mni_Beng",
    "Halh Mongolian": "khk_Cyrl",
    "Mossi": "mos_Latn",
    "Maori": "mri_Latn",
    "Burmese": "mya_Mymr",
    "Dutch": "nld_Latn",
    "Norwegian Nynorsk": "nno_Latn",
    "Norwegian Bokmål": "nob_Latn",
    "Nepali": "npi_Deva",
    "Northern Sotho": "nso_Latn",
    "Nuer": "nus_Latn",
    "Nyanja": "nya_Latn",
    "Occitan": "oci_Latn",
    "West Central Oromo": "gaz_Latn",
    "Odia": "ory_Orya",
    "Pangasinan": "pag_Latn",
    "Eastern Panjabi": "pan_Guru",
    "Papiamento": "pap_Latn",
    "Western Persian": "pes_Arab",
    "Polish": "pol_Latn",
    "Portuguese": "por_Latn",
    "Dari": "prs_Arab",
    "Southern Pashto": "pbt_Arab",
    "Ayacucho Quechua": "quy_Latn",
    "Romanian": "ron_Latn",
    "Rundi": "run_Latn",
    "Russian": "rus_Cyrl",
    "Sango": "sag_Latn",
    "Sanskrit": "san_Deva",
    "Santali": "sat_Olck",
    "Sicilian": "scn_Latn",
    "Shan": "shn_Mymr",
    "Sinhala": "sin_Sinh",
    "Slovak": "slk_Latn",
    "Slovenian": "slv_Latn",
    "Samoan": "smo_Latn",
    "Shona": "sna_Latn",
    "Sindhi": "snd_Arab",
    "Somali": "som_Latn",
    "Southern Sotho": "sot_Latn",
    "Spanish": "spa_Latn",
    "Tosk Albanian": "als_Latn",
    "Sardinian": "srd_Latn",
    "Serbian": "srp_Cyrl",
    "Swati": "ssw_Latn",
    "Sundanese": "sun_Latn",
    "Swedish": "swe_Latn",
    "Swahili": "swh_Latn",
    "Silesian": "szl_Latn",
    "Tamil": "tam_Taml",
    "Tatar": "tat_Cyrl",
    "Telugu": "tel_Telu",
    "Tajik": "tgk_Cyrl",
    "Tagalog": "tgl_Latn",
    "Thai": "tha_Thai",
    "Tigrinya": "tir_Ethi",
    "Tamasheq (Latin script)": "taq_Latn",
    "Tamasheq (Tifinagh script)": "taq_Tfng",
    "Tok Pisin": "tpi_Latn",
    "Tswana": "tsn_Latn",
    "Tsonga": "tso_Latn",
    "Turkmen": "tuk_Latn",
    "Tumbuka": "tum_Latn",
    "Turkish": "tur_Latn",
    "Twi": "twi_Latn",
    "Central Atlas Tamazight": "tzm_Tfng",
    "Uyghur": "uig_Arab",
    "Ukrainian": "ukr_Cyrl",
    "Umbundu": "umb_Latn",
    "Urdu": "urd_Arab",
    "Northern Uzbek": "uzn_Latn",
    "Venetian": "vec_Latn",
    "Vietnamese": "vie_Latn",
    "Waray": "war_Latn",
    "Wolof": "wol_Latn",
    "Xhosa": "xho_Latn",
    "Eastern Yiddish": "ydd_Hebr",
    "Yoruba": "yor_Latn",
    "Yue Chinese": "yue_Hant",
    "Chinese (Simplified)": "zho_Hans",
    "Chinese (Traditional)": "zho_Hant",
    "Standard Malay": "zsm_Latn",
    "Zulu": "zul_Latn",
}


class ModelManager:
    """Manages the NLLB translation model lifecycle.

    This class implements a singleton-like pattern to ensure the model
    is loaded only once and kept in memory for reuse across requests.
    """

    _instance: "ModelManager | None" = None
    _model: "AutoModelForSeq2SeqLM | None" = None
    _tokenizer: "AutoTokenizer | None" = None
    _is_loaded: bool = False

    def __new__(cls) -> "ModelManager":
        """Ensure only one instance of ModelManager exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the ModelManager."""
        self._cache_dir = DEFAULT_CACHE_DIR

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
        return self._cache_dir / MODEL_NAME.replace("/", "--")

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
        required_files = ["config.json", "tokenizer_config.json"]
        return all((self.model_path / f).exists() for f in required_files)

    def download_model(self, force: bool = False) -> Path:
        """Download the NLLB model to the local cache.

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

        logger.info(f"Downloading model {MODEL_NAME} to {self._cache_dir}")

        try:
            # Ensure cache directory exists
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Download model snapshot
            downloaded_path = snapshot_download(
                repo_id=MODEL_NAME,
                local_dir=self.model_path,
                local_dir_use_symlinks=False,
            )

            logger.info(f"Model downloaded successfully to {downloaded_path}")
            return Path(downloaded_path)

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            raise RuntimeError(f"Failed to download model {MODEL_NAME}: {e}") from e

    def load_model(self) -> tuple["AutoModelForSeq2SeqLM", "AutoTokenizer"]:
        """Load the model and tokenizer into memory.

        If the model is already loaded, returns the cached instances.
        If the model is not downloaded, downloads it first.

        Returns:
            Tuple of (model, tokenizer).

        Raises:
            RuntimeError: If model loading fails.
        """
        if self._is_loaded and self._model is not None and self._tokenizer is not None:
            logger.debug("Returning cached model and tokenizer")
            return self._model, self._tokenizer

        # Import here to avoid slow startup when not using the model
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        # Ensure model is downloaded
        if not self.is_downloaded:
            logger.info("Model not found locally, downloading...")
            self.download_model()

        logger.info(f"Loading model from {self.model_path}")

        try:
            # Load tokenizer
            tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            logger.info("Tokenizer loaded successfully")

            # Load model
            model: AutoModelForSeq2SeqLM = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            logger.info("Model loaded successfully")

            # Store in instance variables for caching
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

    def get_model(self) -> "AutoModelForSeq2SeqLM":
        """Get the loaded model, loading it if necessary.

        Returns:
            The loaded model.

        Raises:
            RuntimeError: If model is not loaded and loading fails.
        """
        if not self._is_loaded or self._model is None:
            self.load_model()
        return self._model  # type: ignore[return-value]

    def get_tokenizer(self) -> "AutoTokenizer":
        """Get the loaded tokenizer, loading it if necessary.

        Returns:
            The loaded tokenizer.

        Raises:
            RuntimeError: If tokenizer is not loaded and loading fails.
        """
        if not self._is_loaded or self._tokenizer is None:
            self.load_model()
        return self._tokenizer  # type: ignore[return-value]

    def verify_model_files(self) -> dict[str, bool]:
        """Verify that all necessary model files are present.

        Returns:
            Dictionary mapping filename to whether it exists.
        """
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

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages.

        Args:
            text: The text to translate.
            source_lang: Source language NLLB code (e.g., "eng_Latn").
            target_lang: Target language NLLB code (e.g., "fra_Latn").

        Returns:
            The translated text.

        Raises:
            RuntimeError: If model loading fails.
        """
        model, tokenizer = self.load_model()
        tokenizer.src_lang = source_lang
        inputs = tokenizer(text, return_tensors="pt")
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(target_lang),
            max_length=512,
        )
        return tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]


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

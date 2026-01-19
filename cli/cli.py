"""CLI script for model management operations.

This module provides command-line utilities for:
- Downloading translation models (NLLB, TranslateGemma)
- Verifying model files
- Checking model status
- Translating text
"""

import argparse
import logging
import sys
import time

from core.model import (
    DEFAULT_MODEL_ID,
    MODEL_REGISTRY,
    get_available_models,
    get_model_info,
    get_model_manager,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI output."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_model_id(args: argparse.Namespace) -> str:
    """Get the model_id from args, defaulting to DEFAULT_MODEL_ID."""
    return getattr(args, "model", None) or DEFAULT_MODEL_ID


def validate_model_id(model_id: str) -> bool:
    """Validate that a model_id is recognized."""
    if model_id not in MODEL_REGISTRY:
        print(
            f"✗ Unknown model: '{model_id}'",
            file=sys.stderr,
        )
        print(
            f"  Available models: {', '.join(MODEL_REGISTRY.keys())}",
            file=sys.stderr,
        )
        return False
    return True


def cmd_models(args: argparse.Namespace) -> int:
    """List available translation models."""
    models = get_available_models()
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    print("Available translation models:\n")

    for info in models:
        backend = manager.get_backend(info.model_id)
        status = "✓ Downloaded" if backend.is_downloaded else "○ Not downloaded"
        loaded = " (loaded)" if backend.is_loaded else ""
        auth = " [requires HF token]" if info.requires_auth else ""

        print(f"  {info.model_id}")
        print(f"    Name: {info.display_name}")
        print(f"    Repo: {info.repo_id}")
        print(f"    Size: {info.size_estimate}")
        print(f"    Status: {status}{loaded}{auth}")
        print(f"    {info.description}")
        print()

    print(f"Default model: {DEFAULT_MODEL_ID}")
    print("\nUse --model <id> with other commands to select a model.")
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    """Download a translation model."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)

    print(f"Model: {info.display_name} ({info.repo_id})")
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Model path: {backend.model_path}")

    if info.requires_auth:
        print("\n⚠ This model requires accepting the license on Hugging Face")
        print(f"  Visit: https://huggingface.co/{info.repo_id}")
        print("  Set HF_TOKEN environment variable with your token.")

    print()

    if backend.is_downloaded and not args.force:
        print("✓ Model already downloaded.")
        print("  Use --force to re-download.")
        return 0

    print(f"Downloading model... (this may take a while, {info.size_estimate})")
    try:
        backend.download_model(force=args.force)
        print()
        print("✓ Model downloaded successfully!")
        return 0
    except RuntimeError as e:
        print(f"✗ Download failed: {e}", file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify model files are present."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)

    print(f"Model: {info.display_name}")
    print(f"Model path: {backend.model_path}")
    print()

    if not backend.model_path.exists():
        print("✗ Model directory does not exist.")
        print("  Run 'download' command first.")
        return 1

    results = backend.verify_model_files()

    all_present = True
    for filename, exists in results.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")
        if not exists:
            all_present = False

    print()
    if all_present:
        print("✓ All required files are present.")
        return 0
    else:
        print("✗ Some files are missing.")
        return 1


def cmd_status(args: argparse.Namespace) -> int:
    """Show model status."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)

    print(f"Model: {info.display_name} ({info.repo_id})")
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Model path: {backend.model_path}")
    print()

    downloaded = backend.is_downloaded
    print(f"Downloaded: {'Yes' if downloaded else 'No'}")
    print(f"Loaded in memory: {'Yes' if backend.is_loaded else 'No'}")

    if downloaded:
        total_size = 0
        for file in backend.model_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        size_mb = total_size / (1024 * 1024)
        print(f"Total size: {size_mb:.1f} MB")

    return 0


def cmd_load_test(args: argparse.Namespace) -> int:
    """Test loading a model."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)

    print(f"Testing model load for {info.display_name}...")
    print()

    try:
        result = backend.load_model()
        if info.model_type == "seq2seq":
            model, tokenizer = result
            print(f"✓ Model loaded: {type(model).__name__}")
            print(f"✓ Tokenizer loaded: {type(tokenizer).__name__}")
        else:
            model, processor = result
            print(f"✓ Model loaded: {type(model).__name__}")
            print(f"✓ Processor loaded: {type(processor).__name__}")
        print()
        print("Model is ready for translation!")
        return 0
    except RuntimeError as e:
        print(f"✗ Load failed: {e}", file=sys.stderr)
        return 1


def cmd_delete(args: argparse.Namespace) -> int:
    """Delete a downloaded model."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)

    print(f"Model: {info.display_name} ({info.repo_id})")
    print(f"Model path: {backend.model_path}")
    print()

    if not backend.is_downloaded:
        print("✓ Model not downloaded, nothing to delete.")
        return 0

    try:
        backend.delete_model()
        print("✓ Model deleted successfully!")
        return 0
    except RuntimeError as e:
        print(f"✗ Deletion failed: {e}", file=sys.stderr)
        return 1


def cmd_languages(args: argparse.Namespace) -> int:
    """List all supported languages and their codes."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()
    info = get_model_info(model_id)
    language_codes = manager.get_language_codes(model_id)

    print(f"Supported languages for {info.display_name}:\n")

    # Find max language name length for alignment
    max_name_len = max(len(name) for name in language_codes)

    for name, code in sorted(language_codes.items()):
        print(f"  {name:<{max_name_len}}  {code}")

    print(f"\nTotal: {len(language_codes)} languages")
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    """Translate text between languages."""
    model_id = get_model_id(args)
    if not validate_model_id(model_id):
        return 1

    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    backend = manager.get_backend(model_id)
    language_codes = backend.get_language_codes()
    valid_codes = set(language_codes.values())

    if args.source not in valid_codes:
        print(
            f"✗ Unsupported source language code for {model_id}: '{args.source}'",
            file=sys.stderr,
        )
        print(
            f"  Use 'bab languages --model {model_id}' to see supported codes.",
            file=sys.stderr,
        )
        return 1

    if args.target not in valid_codes:
        print(
            f"✗ Unsupported target language code for {model_id}: '{args.target}'",
            file=sys.stderr,
        )
        print(
            f"  Use 'bab languages --model {model_id}' to see supported codes.",
            file=sys.stderr,
        )
        return 1

    if not backend.is_downloaded:
        print(f"✗ Model '{model_id}' not downloaded.", file=sys.stderr)
        print(f"  Run 'bab download --model {model_id}' first.", file=sys.stderr)
        return 1

    try:
        start_time = time.perf_counter()
        translated = backend.translate(args.text, args.source, args.target)
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"Translation completed in {elapsed_time:.3f} seconds")
        print(translated)
        return 0
    except RuntimeError as e:
        print(f"✗ Translation failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    # Parent parser for shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parent_parser.add_argument(
        "--cache-dir",
        type=str,
        help="Custom cache directory for model storage",
    )
    parent_parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=DEFAULT_MODEL_ID,
        choices=list(MODEL_REGISTRY.keys()),
        help=f"Translation model to use (default: {DEFAULT_MODEL_ID})",
    )

    parser = argparse.ArgumentParser(
        prog="bab",
        description="Bab - Multi-Model Translation Manager",
        parents=[parent_parser],
    )

    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        dest="command",
    )

    # Models command (list available models)
    models_parser = subparsers.add_parser(
        "models",
        help="List available translation models",
        parents=[parent_parser],
    )
    models_parser.set_defaults(func=cmd_models)

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download a translation model",
        parents=[parent_parser],
    )
    download_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force re-download even if model exists",
    )
    download_parser.set_defaults(func=cmd_download)

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify model files are present",
        parents=[parent_parser],
    )
    verify_parser.set_defaults(func=cmd_verify)

    status_parser = subparsers.add_parser(
        "status",
        help="Show model status",
        parents=[parent_parser],
    )
    status_parser.set_defaults(func=cmd_status)

    languages_parser = subparsers.add_parser(
        "languages",
        help="List all supported languages and their codes",
        parents=[parent_parser],
    )
    languages_parser.set_defaults(func=cmd_languages)

    load_parser = subparsers.add_parser(
        "load-test",
        help="Test loading the model into memory",
        parents=[parent_parser],
    )
    load_parser.set_defaults(func=cmd_load_test)

    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete the downloaded model from disk",
        parents=[parent_parser],
    )
    delete_parser.set_defaults(func=cmd_delete)

    translate_parser = subparsers.add_parser(
        "translate",
        help="Translate text between languages",
        parents=[parent_parser],
    )
    translate_parser.add_argument(
        "text",
        help="Text to translate",
    )
    translate_parser.add_argument(
        "-s",
        "--source",
        required=True,
        help="Source language code (required)",
    )
    translate_parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target language code (required)",
    )
    translate_parser.set_defaults(func=cmd_translate)

    args = parser.parse_args()

    setup_logging(args.verbose)

    if not args.command:
        from cli.interactive import run_interactive

        run_interactive()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

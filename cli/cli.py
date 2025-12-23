"""CLI script for model management operations.

This module provides command-line utilities for:
- Downloading the NLLB model
- Verifying model files
- Checking model status
"""

import argparse
import logging
import sys
import time

from core.model import LANGUAGE_CODES, MODEL_NAME, get_model_manager


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for CLI output."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_download(args: argparse.Namespace) -> int:
    """Download the NLLB model."""
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    print(f"Model: {MODEL_NAME}")
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Model path: {manager.model_path}")
    print()

    if manager.is_downloaded and not args.force:
        print("✓ Model already downloaded.")
        print("  Use --force to re-download.")
        return 0

    print("Downloading model... (this may take a while, ~2.5GB)")
    try:
        manager.download_model(force=args.force)
        print()
        print("✓ Model downloaded successfully!")
        return 0
    except RuntimeError as e:
        print(f"✗ Download failed: {e}", file=sys.stderr)
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify model files are present."""
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    print(f"Model path: {manager.model_path}")
    print()

    if not manager.model_path.exists():
        print("✗ Model directory does not exist.")
        print("  Run 'download' command first.")
        return 1

    results = manager.verify_model_files()

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
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    print(f"Model: {MODEL_NAME}")
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Model path: {manager.model_path}")
    print()

    downloaded = manager.is_downloaded
    print(f"Downloaded: {'Yes' if downloaded else 'No'}")
    print(f"Loaded in memory: {'Yes' if manager.is_loaded else 'No'}")

    if downloaded:
        # Calculate approximate size
        total_size = 0
        for file in manager.model_path.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        size_mb = total_size / (1024 * 1024)
        print(f"Total size: {size_mb:.1f} MB")

    return 0


def cmd_load_test(args: argparse.Namespace) -> int:
    """Test loading the model."""
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    print("Testing model load...")
    print()

    try:
        model, tokenizer = manager.load_model()
        print(f"✓ Model loaded: {type(model).__name__}")
        print(f"✓ Tokenizer loaded: {type(tokenizer).__name__}")
        print()
        print("Model is ready for translation!")
        return 0
    except RuntimeError as e:
        print(f"✗ Load failed: {e}", file=sys.stderr)
        return 1


def cmd_languages(args: argparse.Namespace) -> int:
    """List all supported languages and their codes."""
    print("Supported languages:\n")

    # Find max language name length for alignment
    max_name_len = max(len(name) for name in LANGUAGE_CODES)

    for name, code in sorted(LANGUAGE_CODES.items()):
        print(f"  {name:<{max_name_len}}  {code}")

    print(f"\nTotal: {len(LANGUAGE_CODES)} languages")
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    """Translate text between languages."""
    manager = get_model_manager()

    if args.cache_dir:
        manager.cache_dir = args.cache_dir

    valid_codes = set(LANGUAGE_CODES.values())

    if args.source not in valid_codes:
        print(f"✗ Unsupported source language code: '{args.source}'", file=sys.stderr)
        print("  Use 'bab languages' to see supported language codes.", file=sys.stderr)
        return 1

    if args.target not in valid_codes:
        print(f"✗ Unsupported target language code: '{args.target}'", file=sys.stderr)
        print("  Use 'bab languages' to see supported language codes.", file=sys.stderr)
        return 1

    if not manager.is_downloaded:
        print("✗ Model not downloaded.", file=sys.stderr)
        print("  Run 'bab download' first.", file=sys.stderr)
        return 1

    try:
        start_time = time.perf_counter()
        translated = manager.translate(args.text, args.source, args.target)
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

    parser = argparse.ArgumentParser(
        prog="bab",
        description="Bab - NLLB Translation Model Manager",
        parents=[parent_parser],
    )

    subparsers = parser.add_subparsers(
        title="commands",
        description="Available commands",
        dest="command",
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download",
        help="Download the NLLB model",
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

"""Interactive terminal mode for Bab translation.

This module provides a REPL-style interface for:
- Setting source/target languages with autocomplete
- Selecting translation model
- Translating text interactively
- Viewing model status
"""

import os
import random
from pathlib import Path

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.interactive.completers import CommandCompleter, LanguageCompleter
from core.model import (
    DEFAULT_MODEL_ID,
    MODEL_REGISTRY,
    get_available_models,
    get_model_info,
    get_model_manager,
)
from core.preferences import get_preferences_manager


class InteractiveSession:
    """Manages an interactive translation session."""

    def __init__(self):
        self.console = Console()
        self.manager = get_model_manager()
        self.preferences = get_preferences_manager()

        # Load saved model preference
        saved_model = self.preferences.get("cli:model_id")
        self.model_id = (
            saved_model if saved_model in MODEL_REGISTRY else DEFAULT_MODEL_ID
        )

        # Initialize language codes for current model
        self._update_language_codes()

        self.command_completer = CommandCompleter()

        history_path = Path.home() / ".cache" / "bab" / "history"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(history_path)))

        # Load saved language preferences
        valid_codes = set(self.language_codes.values())
        saved_source = self.preferences.get("cli:source_lang")
        self.source_lang = saved_source if saved_source in valid_codes else None
        saved_target = self.preferences.get("cli:target_lang")
        self.target_lang = saved_target if saved_target in valid_codes else None

    def _update_language_codes(self):
        """Update language codes and completer for current model."""
        self.language_codes = self.manager.get_language_codes(self.model_id)
        self.code_to_name = {v: k for k, v in self.language_codes.items()}
        self.lang_completer = LanguageCompleter(self.language_codes)

    def _get_language_name(self, code: str) -> str:
        """Get the human-readable name for a language code."""
        return self.code_to_name.get(code, code)

    def _format_lang_setting(self, label: str, code: str | None) -> str:
        """Format a language setting for display."""
        if code:
            name = self._get_language_name(code)
            return f"{label}: {name} ({code})"
        return f"{label}: [dim]not set[/dim]"

    def print_welcome(self):
        """Print welcome message and instructions."""
        banner = Text()
        banner.append("╔═══╗\n", style="dim")
        banner.append("║ ", style="dim")
        banner.append("B A B", style="bold")
        banner.append("\n", style="dim")
        banner.append("╚═══╝", style="dim")

        self.console.print()
        self.console.print(banner)
        self.console.print()

        # Show current model
        model_info = get_model_info(self.model_id)
        self.console.print(
            f"  Model: [bold]{model_info.display_name}[/bold]",
            markup=True,
        )

        self.console.print(
            self._format_lang_setting("  Source", self.source_lang), markup=True
        )
        self.console.print(
            self._format_lang_setting("  Target", self.target_lang), markup=True
        )
        self.console.print()

        self.console.print(
            "[dim]Type [/dim][bold white]/source[/bold white][dim] or [/dim]"
            "[bold white]/target[/bold white][dim] to set languages",
            markup=True,
        )

        self.console.print(
            "[dim]Type [/dim][bold white]/model[/bold white][dim] to change model, "
            "[/dim][bold white]/exit[/bold white][dim] to exit.[/dim]",
            markup=True,
        )
        self.console.print(
            "[dim]Type [/dim][bold white]/help[/bold white]"
            "[dim] for all commands.[/dim]",
            markup=True,
        )
        self.console.print()
        self.console.print("[dim]Enter text to translate.[/dim]")
        self.console.print()

    def print_help(self):
        """Print available commands."""
        help_table = Table(show_header=True, header_style="bold", box=None)
        help_table.add_column("Command", style="bold")
        help_table.add_column("Description")

        commands = [
            ("/model", "Select translation model"),
            ("/source", "Set source language (with autocomplete)"),
            ("/target", "Set target language (with autocomplete)"),
            ("/swap", "Swap source and target languages"),
            ("/status", "Show model and session status"),
            ("/languages", "List all available language codes"),
            ("/models", "List available translation models"),
            ("/clear", "Clear screen and history"),
            ("/help", "Show this help message"),
            ("/quit, /exit, /q", "Exit interactive mode"),
            ("<text>", "Translate the entered text"),
        ]

        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        self.console.print()
        self.console.print(help_table)
        self.console.print()

    def set_model(self):
        """Prompt user to select a translation model."""
        models = get_available_models()

        self.console.print()
        self.console.print("[bold]Available models:[/bold]", markup=True)
        self.console.print()

        for i, info in enumerate(models, 1):
            backend = self.manager.get_backend(info.model_id)
            status = "✓" if backend.is_downloaded else "○"
            current = " [current]" if info.model_id == self.model_id else ""
            auth = " [requires HF token]" if info.requires_auth else ""

            self.console.print(
                f"  {i}. {status} [bold]{info.model_id}[/bold] - "
                f"{info.display_name}{current}{auth}",
                markup=True,
            )

        self.console.print()
        self.console.print(
            "[dim]Enter model number or ID:[/dim]",
            markup=True,
        )

        try:
            choice = prompt("model> ").strip()
            if not choice:
                return

            # Try parsing as number first
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    new_model_id = models[idx].model_id
                else:
                    self.console.print(
                        f"✗ Invalid choice: {choice}",
                        markup=True,
                    )
                    return
            except ValueError:
                # Try as model ID
                if choice in MODEL_REGISTRY:
                    new_model_id = choice
                else:
                    self.console.print(
                        f"✗ Unknown model: '{choice}'",
                        markup=True,
                    )
                    return

            # Switch model
            self.model_id = new_model_id
            self.preferences.set("cli:model_id", new_model_id)
            self._update_language_codes()

            # Clear language settings if they're invalid for new model
            valid_codes = set(self.language_codes.values())
            if self.source_lang and self.source_lang not in valid_codes:
                self.source_lang = None
                self.preferences.delete("cli:source_lang")
            if self.target_lang and self.target_lang not in valid_codes:
                self.target_lang = None
                self.preferences.delete("cli:target_lang")

            model_info = get_model_info(new_model_id)
            self.console.print(
                f"✓ Switched to [bold]{model_info.display_name}[/bold]",
                markup=True,
            )

            if not self.manager.get_backend(new_model_id).is_downloaded:
                self.console.print(
                    "[dim]  Note: Model not downloaded. "
                    "Run 'bab download --model {}' first.[/dim]".format(new_model_id),
                    markup=True,
                )

        except (KeyboardInterrupt, EOFError):
            self.console.print("[dim]Cancelled[/dim]", markup=True)

    def set_source_language(self):
        """Prompt user to set source language with autocomplete."""
        self.console.print(
            "[dim]Enter source language (Tab for autocomplete):[/dim]",
            markup=True,
        )
        try:
            lang = prompt("source> ", completer=self.lang_completer).strip()
            if lang:
                valid_codes = set(self.language_codes.values())
                if lang in valid_codes:
                    self.source_lang = lang
                    self.preferences.set("cli:source_lang", lang)
                    name = self._get_language_name(lang)
                    self.console.print(
                        f"✓ Source set to [bold]{lang}[/bold] ({name})",
                        markup=True,
                    )
                else:
                    self.console.print(
                        f"✗ Unknown language code: '{lang}'", markup=True
                    )
                    self.console.print(
                        "[dim]  Use /languages to see available codes.[/dim]",
                        markup=True,
                    )
        except (KeyboardInterrupt, EOFError):
            self.console.print("[dim]Cancelled[/dim]", markup=True)

    def swap_languages(self):
        """Swap source and target languages."""
        if not self.source_lang and not self.target_lang:
            self.console.print(
                "⚠ Both source and target languages are not set.",
                markup=True,
            )
            return

        self.source_lang, self.target_lang = self.target_lang, self.source_lang

        if self.source_lang:
            self.preferences.set("cli:source_lang", self.source_lang)
        else:
            self.preferences.delete("cli:source_lang")

        if self.target_lang:
            self.preferences.set("cli:target_lang", self.target_lang)
        else:
            self.preferences.delete("cli:target_lang")

        source_name = self._get_language_name(self.source_lang)
        source_display = (
            f"[bold]{self.source_lang}[/bold] ({source_name})"
            if self.source_lang
            else "[dim]not set[/dim]"
        )
        target_name = self._get_language_name(self.target_lang)
        target_display = (
            f"[bold]{self.target_lang}[/bold] ({target_name})"
            if self.target_lang
            else "[dim]not set[/dim]"
        )

        self.console.print(
            f"✓ Languages swapped: {source_display} → {target_display}",
            markup=True,
        )

    def set_target_language(self):
        """Prompt user to set target language with autocomplete."""
        self.console.print(
            "[dim]Enter target language (Tab for autocomplete):[/dim]",
            markup=True,
        )
        try:
            lang = prompt("target> ", completer=self.lang_completer).strip()
            if lang:
                valid_codes = set(self.language_codes.values())
                if lang in valid_codes:
                    self.target_lang = lang
                    self.preferences.set("cli:target_lang", lang)
                    name = self._get_language_name(lang)
                    self.console.print(
                        f"✓ Target set to [bold]{lang}[/bold] ({name})",
                        markup=True,
                    )
                else:
                    self.console.print(
                        f"✗ Unknown language code: '{lang}'", markup=True
                    )
                    self.console.print(
                        "[dim]  Use /languages to see available codes.[/dim]",
                        markup=True,
                    )
        except (KeyboardInterrupt, EOFError):
            self.console.print("[dim]Cancelled[/dim]", markup=True)

    def translate_text(self, text: str):
        """Translate the given text and display result."""
        if not self.source_lang:
            self.console.print(
                "⚠ Source language not set. Use [bold]/source[/bold] first.",
                markup=True,
            )
            return

        if not self.target_lang:
            self.console.print(
                "⚠ Target language not set. Use [bold]/target[/bold] first.",
                markup=True,
            )
            return

        backend = self.manager.get_backend(self.model_id)

        if not backend.is_downloaded:
            self.console.print(
                f"✗ Model '{self.model_id}' not downloaded.", markup=True
            )
            self.console.print(
                f"[dim]  Run 'bab download --model {self.model_id}' "
                "from the command line first.[/dim]",
                markup=True,
            )
            return

        try:
            with self.console.status(
                "", spinner="simpleDotsScrolling", spinner_style="white"
            ):
                translated = backend.translate(
                    text, self.source_lang, self.target_lang
                )

            source_name = self._get_language_name(self.source_lang)
            target_name = self._get_language_name(self.target_lang)

            result_panel = Panel(
                translated,
                title=f"[dim]{source_name}[/dim] → [bold]{target_name}[/bold]",
                border_style="white",
                padding=(0, 1),
            )
            self.console.print(result_panel)

        except RuntimeError as e:
            self.console.print(f"✗ Translation failed: {e}", markup=True)

    def show_status(self):
        """Show current model and session status."""
        self.console.print()

        status_table = Table(
            show_header=True, header_style="bold", box=None, padding=(0, 2)
        )
        status_table.add_column("Setting", style="dim")
        status_table.add_column("Value")

        # Model info
        model_info = get_model_info(self.model_id)
        status_table.add_row("Model", f"{model_info.display_name} ({self.model_id})")
        status_table.add_row("Repo", model_info.repo_id)
        status_table.add_row("", "")

        if self.source_lang:
            source_name = self._get_language_name(self.source_lang)
            source_val = f"{self.source_lang} ({source_name})"
        else:
            source_val = "[dim]not set[/dim]"

        if self.target_lang:
            target_name = self._get_language_name(self.target_lang)
            target_val = f"{self.target_lang} ({target_name})"
        else:
            target_val = "[dim]not set[/dim]"

        status_table.add_row("Source Language", source_val)
        status_table.add_row("Target Language", target_val)
        status_table.add_row("", "")

        backend = self.manager.get_backend(self.model_id)
        status_table.add_row("Cache Directory", str(self.manager.cache_dir))

        downloaded = backend.is_downloaded
        downloaded_status = "[bold]Yes[/bold]" if downloaded else "No"
        status_table.add_row("Downloaded", downloaded_status)

        loaded = backend.is_loaded
        loaded_status = "[bold]Yes[/bold]" if loaded else "[dim]No[/dim]"
        status_table.add_row("Loaded in Memory", loaded_status)

        if downloaded:
            total_size = 0
            for file in backend.model_path.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
            size_mb = total_size / (1024 * 1024)
            status_table.add_row("Model Size", f"{size_mb:.1f} MB")

        self.console.print(status_table)
        self.console.print()

    def show_languages(self):
        """Display available languages in a formatted table."""
        model_info = get_model_info(self.model_id)

        table = Table(
            show_header=True,
            header_style="bold",
            title=f"Languages for {model_info.display_name}",
            title_style="bold",
        )

        table.add_column("Language", style="white")
        table.add_column("Code", style="bold")
        table.add_column("Language", style="white")
        table.add_column("Code", style="bold")

        sorted_langs = sorted(self.language_codes.items())
        mid = (len(sorted_langs) + 1) // 2

        left_col = sorted_langs[:mid]
        right_col = sorted_langs[mid:]

        for i in range(mid):
            left_name, left_code = left_col[i]
            if i < len(right_col):
                right_name, right_code = right_col[i]
                table.add_row(left_name, left_code, right_name, right_code)
            else:
                table.add_row(left_name, left_code, "", "")

        self.console.print()
        self.console.print(table)
        self.console.print(f"\n[dim]Total: {len(self.language_codes)} languages[/dim]")
        self.console.print()

    def show_models(self):
        """Display available models."""
        models = get_available_models()

        self.console.print()
        self.console.print("[bold]Available translation models:[/bold]", markup=True)
        self.console.print()

        for info in models:
            backend = self.manager.get_backend(info.model_id)
            status = "✓ Downloaded" if backend.is_downloaded else "○ Not downloaded"
            loaded = " (loaded)" if backend.is_loaded else ""
            current = " [bold cyan]← current[/bold cyan]" if info.model_id == self.model_id else ""
            auth = " [yellow][HF token required][/yellow]" if info.requires_auth else ""

            self.console.print(
                f"  [bold]{info.model_id}[/bold] - {info.display_name}{current}",
                markup=True,
            )
            self.console.print(f"    {status}{loaded}{auth}", markup=True)
            self.console.print(f"    Size: {info.size_estimate}", markup=True)
            self.console.print(f"    [dim]{info.description}[/dim]", markup=True)
            self.console.print()

    def clear_screen(self):
        """Clear terminal screen and reset command history."""
        os.system("clear" if os.name != "nt" else "cls")
        history_path = Path.home() / ".cache" / "bab" / "history"
        if history_path.exists():
            history_path.unlink()
        self.session = PromptSession(history=FileHistory(str(history_path)))
        self.print_welcome()

    def run(self):
        """Main REPL loop."""
        self.print_welcome()

        while True:
            try:
                model_info = get_model_info(self.model_id)
                model_short = model_info.model_id

                if self.source_lang and self.target_lang:
                    source_name = self._get_language_name(self.source_lang)
                    target_name = self._get_language_name(self.target_lang)

                    prompt_text = f"[{source_name} → {target_name}] {model_short}> "
                else:
                    prompt_text = f"{model_short}> "

                user_input = self.session.prompt(
                    prompt_text, completer=self.command_completer
                ).strip()

                if not user_input:
                    continue

                if user_input in ("/quit", "/exit", "/q"):
                    break
                elif user_input == "/model":
                    self.set_model()
                elif user_input == "/source":
                    self.set_source_language()
                elif user_input == "/target":
                    self.set_target_language()
                elif user_input == "/swap":
                    self.swap_languages()
                elif user_input == "/status":
                    self.show_status()
                elif user_input == "/languages":
                    self.show_languages()
                elif user_input == "/models":
                    self.show_models()
                elif user_input == "/clear":
                    self.clear_screen()
                elif user_input == "/help":
                    self.print_help()
                elif user_input.startswith("/"):
                    self.console.print(
                        f"Unknown command: {user_input}",
                        markup=True,
                    )
                    self.console.print(
                        "[dim]Type /help for available commands.[/dim]",
                        markup=True,
                    )
                else:
                    self.translate_text(user_input)

            except KeyboardInterrupt:
                self.console.print("(To exit, use /exit /quit or /q)")
                continue
            except EOFError:
                break

        goodbye_phrases = [
            "Goodbye!",
            "¡Adiós!",
            "Au revoir!",
            "Tchau!",
            "Ciao!",
        ]
        farewell = random.choice(goodbye_phrases)
        self.console.print(f"\n[dim]{farewell}[/dim]", markup=True)
        self.console.print()


def run_interactive():
    """Entry point for interactive mode."""
    session = InteractiveSession()
    session.run()

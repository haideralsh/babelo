"""Interactive terminal mode for Bab translation.

This module provides a REPL-style interface for:
- Setting source/target languages with autocomplete
- Translating text interactively
- Viewing model status
"""

import random
from pathlib import Path

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.interactive.completers import CommandCompleter, LanguageCompleter
from core.model import LANGUAGE_CODES, MODEL_NAME, get_model_manager
from core.preferences import get_preferences_manager


class InteractiveSession:
    """Manages an interactive translation session."""

    def __init__(self):
        self.console = Console()
        self.manager = get_model_manager()

        self.lang_completer = LanguageCompleter(LANGUAGE_CODES)
        self.command_completer = CommandCompleter()

        self.code_to_name = {v: k for k, v in LANGUAGE_CODES.items()}
        history_path = Path.home() / ".cache" / "bab" / "history"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        self.session = PromptSession(history=FileHistory(str(history_path)))

        self.preferences = get_preferences_manager()
        valid_codes = set(LANGUAGE_CODES.values())
        saved_source = self.preferences.get("cli:source_lang")
        self.source_lang = saved_source if saved_source in valid_codes else None
        saved_target = self.preferences.get("cli:target_lang")
        self.target_lang = saved_target if saved_target in valid_codes else None

    def _get_language_name(self, code: str) -> str:
        """Get the human-readable name for a language code."""
        return self.code_to_name.get(code, code)

    def _format_lang_setting(self, label: str, code: str | None) -> str:
        """Format a language setting for display."""
        if code:
            name = self._get_language_name(code)
            return f"{label}: [bold]{code}[/bold] ({name})"
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
            "[dim]Type [/dim][bold white]/exit[/bold white][dim] or [/dim]"
            "[bold white]/quit[/bold white][dim] to exit.[/dim]",
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
            ("/source", "Set source language (with autocomplete)"),
            ("/target", "Set target language (with autocomplete)"),
            ("/swap", "Swap source and target languages"),
            ("/status", "Show model and session status"),
            ("/languages", "List all available language codes"),
            ("/help", "Show this help message"),
            ("/quit, /exit, /q", "Exit interactive mode"),
            ("<text>", "Translate the entered text"),
        ]

        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        self.console.print()
        self.console.print(help_table)
        self.console.print()

    def set_source_language(self):
        """Prompt user to set source language with autocomplete."""
        self.console.print(
            "[dim]Enter source language (Tab for autocomplete):[/dim]",
            markup=True,
        )
        try:
            lang = prompt("source> ", completer=self.lang_completer).strip()
            if lang:
                valid_codes = set(LANGUAGE_CODES.values())
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
                valid_codes = set(LANGUAGE_CODES.values())
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

        if not self.manager.is_downloaded:
            self.console.print("✗ Model not downloaded.", markup=True)
            self.console.print(
                "[dim]  Run 'bab download' from the command line first.[/dim]",
                markup=True,
            )
            return

        try:
            with self.console.status("Translating...", spinner="dots"):
                translated = self.manager.translate(
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

        status_table.add_row("Model", MODEL_NAME)
        status_table.add_row("Cache Directory", str(self.manager.cache_dir))

        downloaded = self.manager.is_downloaded
        downloaded_status = "[bold]Yes[/bold]" if downloaded else "No"
        status_table.add_row("Downloaded", downloaded_status)

        loaded = self.manager.is_loaded
        loaded_status = "[bold]Yes[/bold]" if loaded else "[dim]No[/dim]"
        status_table.add_row("Loaded in Memory", loaded_status)

        if downloaded:
            total_size = 0
            for file in self.manager.model_path.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
            size_mb = total_size / (1024 * 1024)
            status_table.add_row("Model Size", f"{size_mb:.1f} MB")

        self.console.print(status_table)
        self.console.print()

    def show_languages(self):
        """Display available languages in a formatted table."""
        table = Table(
            show_header=True,
            header_style="bold",
            title="Available Languages",
            title_style="bold",
        )

        table.add_column("Language", style="white")
        table.add_column("Code", style="bold")
        table.add_column("Language", style="white")
        table.add_column("Code", style="bold")

        sorted_langs = sorted(LANGUAGE_CODES.items())
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
        self.console.print(f"\n[dim]Total: {len(LANGUAGE_CODES)} languages[/dim]")
        self.console.print()

    def run(self):
        """Main REPL loop."""
        self.print_welcome()

        while True:
            try:
                if self.source_lang and self.target_lang:
                    source_name = self._get_language_name(self.source_lang)
                    target_name = self._get_language_name(self.target_lang)

                    prompt_text = f"[{source_name} → {target_name}] bab> "
                else:
                    prompt_text = "bab> "

                user_input = self.session.prompt(
                    prompt_text, completer=self.command_completer
                ).strip()

                if not user_input:
                    continue

                if user_input in ("/quit", "/exit", "/q"):
                    break
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

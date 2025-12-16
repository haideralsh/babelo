"""Interactive terminal mode for Bab translation.

This module provides a REPL-style interface for:
- Setting source/target languages with autocomplete
- Translating text interactively
- Viewing model status
"""

from pathlib import Path

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.model import LANGUAGE_CODES, MODEL_NAME, get_model_manager
from core.preferences import get_preferences_manager


class LanguageCompleter(Completer):
    """Custom completer that shows 'Name (code)' but inserts only the code."""

    def __init__(self, language_codes: dict[str, str]):
        # language_codes: {name: code}
        self.languages = [(name, code) for name, code in language_codes.items()]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.lower()
        for name, code in self.languages:
            display = f"{name} ({code})"

            if text in name.lower() or text in code.lower():
                yield Completion(
                    code,  # Insert only the code
                    start_position=-len(document.text_before_cursor),
                    display=display,  # Show full format in dropdown
                )


class InteractiveSession:
    """Manages an interactive translation session."""

    def __init__(self):
        self.console = Console()
        self.manager = get_model_manager()

        self.lang_completer = LanguageCompleter(LANGUAGE_CODES)

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
            return f"{label}: [cyan]{code}[/cyan] ({name})"
        return f"{label}: [dim]not set[/dim]"

    def print_welcome(self):
        """Print welcome message and instructions."""
        banner = Text()
        banner.append("╔═══╗\n", style="cyan")
        banner.append("║ ", style="cyan")
        banner.append("B A B \n", style="bold magenta")
        banner.append("╚═══╝", style="cyan")

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
            "[dim]Type [/dim][cyan]/source[/cyan][dim] or [/dim][cyan]/target[/cyan][dim] to set languages, ",
            markup=True,
        )

        self.console.print(
            "[dim]Type [/dim][cyan]/exit[/cyan][dim] or [/dim][cyan]/quit[/cyan][dim] to exit.[/dim]",
            markup=True,
        )
        self.console.print(
            "[dim]Type [/dim][cyan]/help[/cyan][dim] for all commands.[/dim]",
            markup=True,
        )
        self.console.print()
        self.console.print("[dim]Enter text to translate.[/dim]")
        self.console.print()

    def print_help(self):
        """Print available commands."""
        help_table = Table(show_header=True, header_style="bold cyan", box=None)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")

        commands = [
            ("/source", "Set source language (with autocomplete)"),
            ("/target", "Set target language (with autocomplete)"),
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
                        f"[green]✓[/green] Source set to [cyan]{lang}[/cyan] ({name})",
                        markup=True,
                    )
                else:
                    self.console.print(
                        f"[red]✗[/red] Unknown language code: '{lang}'", markup=True
                    )
                    self.console.print(
                        "[dim]  Use /languages to see available codes.[/dim]",
                        markup=True,
                    )
        except (KeyboardInterrupt, EOFError):
            self.console.print("[dim]Cancelled[/dim]", markup=True)

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
                        f"[green]✓[/green] Target set to [cyan]{lang}[/cyan] ({name})",
                        markup=True,
                    )
                else:
                    self.console.print(
                        f"[red]✗[/red] Unknown language code: '{lang}'", markup=True
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
                "[yellow]⚠[/yellow] Source language not set. "
                "Use [cyan]/source[/cyan] first.",
                markup=True,
            )
            return

        if not self.target_lang:
            self.console.print(
                "[yellow]⚠[/yellow] Target language not set. "
                "Use [cyan]/target[/cyan] first.",
                markup=True,
            )
            return

        if not self.manager.is_downloaded:
            self.console.print("[red]✗[/red] Model not downloaded.", markup=True)
            self.console.print(
                "[dim]  Run 'bab download' from the command line first.[/dim]",
                markup=True,
            )
            return

        try:
            with self.console.status("[cyan]Translating...[/cyan]", spinner="dots"):
                translated = self.manager.translate(
                    text, self.source_lang, self.target_lang
                )

            source_name = self._get_language_name(self.source_lang)
            target_name = self._get_language_name(self.target_lang)

            result_panel = Panel(
                translated,
                title=f"[dim]{source_name}[/dim] → [cyan]{target_name}[/cyan]",
                border_style="green",
                padding=(0, 1),
            )
            self.console.print(result_panel)

        except RuntimeError as e:
            self.console.print(f"[red]✗[/red] Translation failed: {e}", markup=True)

    def show_status(self):
        """Show current model and session status."""
        self.console.print()

        status_table = Table(
            show_header=True, header_style="bold cyan", box=None, padding=(0, 2)
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
        downloaded_status = "[green]Yes[/green]" if downloaded else "[red]No[/red]"
        status_table.add_row("Downloaded", downloaded_status)

        loaded = self.manager.is_loaded
        loaded_status = "[green]Yes[/green]" if loaded else "[dim]No[/dim]"
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
            header_style="bold cyan",
            title="Available Languages",
            title_style="bold",
        )

        table.add_column("Language", style="white")
        table.add_column("Code", style="cyan")
        table.add_column("Language", style="white")
        table.add_column("Code", style="cyan")

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
                    prompt_text = f"[{self.source_lang} → {self.target_lang}] bab> "
                else:
                    prompt_text = "bab> "

                user_input = self.session.prompt(prompt_text, completer=None).strip()

                if not user_input:
                    continue

                if user_input in ("/quit", "/exit", "/q"):
                    break
                elif user_input == "/source":
                    self.set_source_language()
                elif user_input == "/target":
                    self.set_target_language()
                elif user_input == "/status":
                    self.show_status()
                elif user_input == "/languages":
                    self.show_languages()
                elif user_input == "/help":
                    self.print_help()
                elif user_input.startswith("/"):
                    self.console.print(
                        f"[yellow]Unknown command:[/yellow] {user_input}",
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

        self.console.print("\n[dim]Goodbye![/dim]", markup=True)


def run_interactive():
    """Entry point for interactive mode."""
    session = InteractiveSession()
    session.run()

"""Autocomplete providers for the interactive CLI.

Contains completers for language codes and slash commands.
"""

from prompt_toolkit.completion import Completer, Completion


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
                    code,
                    start_position=-len(document.text_before_cursor),
                    display=display,
                )


class CommandCompleter(Completer):
    """Completer for slash commands"""

    COMMANDS = [
        ("/model", "Select translation model"),
        ("/source", "Set source language"),
        ("/target", "Set target language"),
        ("/swap", "Swap source and target languages"),
        ("/status", "Show model and session status"),
        ("/languages", "List all available language codes"),
        ("/models", "List available translation models"),
        ("/clear", "Clear screen and history"),
        ("/help", "Show help message"),
        ("/quit", "Exit interactive mode"),
        ("/exit", "Exit interactive mode"),
        ("/q", "Exit interactive mode"),
    ]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/") and " " not in text:
            for cmd, desc in self.COMMANDS:
                if cmd.startswith(text.lower()):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=f"{cmd} - {desc}",
                    )

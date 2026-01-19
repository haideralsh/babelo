# Babelo

Offline neural machine translation with local-only, on-device inference. Supports multiple translation models:

- **NLLB-200**: Meta's No Language Left Behind model (200+ languages, ~2.5GB)
- **TranslateGemma**: Google's lightweight translation model based on Gemma 3 (55 languages, ~8GB) - Requires a HuggingFace token

## Features

- **Multiple Models**: Choose between NLLB-200 (200+ languages) or TranslateGemma (55 languages)
- **Privacy-First**: Local translation inference, no data sent to external servers
- **Text-to-Speech**: Listen to translations in supported languages in the browser
- **Saved Translations**: Save and revisit your favorite translations
- **CLI & Web Interface**: Use via terminal or web app
- **Fast & Efficient**: Optimized models for speed

## Tech Stack

- **Backend**: Python, FastAPI, HuggingFace Transformers
- **Frontend**: React, TypeScript, Tailwind CSS
- **Models**: Facebook NLLB-200-distilled-600M, Google TranslateGemma-4b-it

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Python package installer and resolver
- ~3GB disk space for NLLB-200, ~8GB for TranslateGemma
- For TranslateGemma: Hugging Face account and token (see below)

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Download a translation model:

   **NLLB-200 (default, ~2.5GB):**
   ```bash
   uv run bab download
   ```

   **TranslateGemma (~8GB):**
   ```bash
   uv run bab download --model translategemma
   ```

   > **Note**: TranslateGemma requires accepting the license on Hugging Face and setting the `HF_TOKEN` environment variable. Visit https://huggingface.co/google/translategemma-4b-it to accept the license.

3. Verify the model files:

   ```bash
   uv run bab verify
   # Or for a specific model:
   uv run bab verify --model translategemma
   ```

4. Run the development server:

   ```bash
   uv run fastapi dev server/main.py
   ```

5. Open http://localhost:8000 in your browser to see the API.

## Available Models

| Model | Languages | Size | Auth Required |
|-------|-----------|------|---------------|
| `nllb` | 200+ | ~2.5GB | No |
| `translategemma` | 55 | ~8GB | Yes (HF token) |

List all models with their download status:
```bash
uv run bab models
```

## CLI Commands

The `bab` CLI provides commands for managing translation models:

### List available models

```bash
uv run bab models
```

### Check model status

```bash
uv run bab status
uv run bab status --model translategemma
```

Shows whether the model is downloaded and loaded, along with storage location and size.

### Download a model

```bash
uv run bab download
uv run bab download --model translategemma
```

Downloads the model to the local cache. Use `--force` to re-download:

```bash
uv run bab download --force
```

### Verify model files

```bash
uv run bab verify
uv run bab verify --model translategemma
```

Checks that all required model files are present.

### List supported languages

```bash
uv run bab languages
uv run bab languages --model translategemma
```

Shows all supported languages for the specified model.

### Test model loading

```bash
uv run bab load-test
uv run bab load-test --model translategemma
```

Loads the model into memory to verify it works correctly.

### Translate text

```bash
uv run bab translate "Hello, world!" -s eng_Latn -t fra_Latn
uv run bab translate "Hello, world!" -s en -t fr --model translategemma
```

Note: Language codes differ between models. Use `bab languages --model <id>` to see available codes.

### Delete a model

```bash
uv run bab delete
uv run bab delete --model translategemma
```

### Custom cache directory

All commands support a custom cache directory:

```bash
uv run bab --cache-dir /path/to/cache status
```

### Interactive mode

Run without arguments to enter interactive mode:

```bash
uv run bab
```

Commands in interactive mode:
- `/model` - Select translation model
- `/source` - Set source language
- `/target` - Set target language
- `/swap` - Swap languages
- `/status` - Show status
- `/languages` - List languages
- `/models` - List models
- `/help` - Show help

## API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key API Endpoints

**Models:**
- `GET /model/list` - List available models
- `GET /model/list/status` - Get status of all models
- `GET /model/status?model_id=nllb` - Get status of a specific model
- `POST /model/download?model_id=nllb` - Download a model
- `POST /model/remove?model_id=nllb` - Remove a model

**Translation:**
- `POST /translate` - Translate text
  ```json
  {
    "text": "Hello",
    "source_language_code": "eng_Latn",
    "target_language_code": "fra_Latn",
    "model_id": "nllb"
  }
  ```

**Languages:**
- `GET /languages?model_id=nllb` - Get supported languages

## TranslateGemma Setup

TranslateGemma requires authentication with Hugging Face:

1. Create a Hugging Face account at https://huggingface.co
2. Visit https://huggingface.co/google/translategemma-4b-it and accept the license
3. Create an access token at https://huggingface.co/settings/tokens
4. Set the `HF_TOKEN` environment variable:

   ```bash
   export HF_TOKEN=hf_your_token_here
   uv run bab download --model translategemma
   ```

## Project Structure

```
babelo/
├── cli/
│   ├── cli.py           # CLI commands
│   └── interactive/     # Interactive mode
├── core/
│   ├── model.py         # Model registry and backends
│   ├── languages.py     # Language code mappings
│   ├── database.py      # Saved translations storage
│   └── preferences.py   # User preferences
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── ModelSelector.tsx
│       │   └── ...
│       ├── hooks/
│       └── utils/
├── server/
│   └── routes/
│       ├── model.py     # Model management endpoints
│       ├── translate.py # Translation endpoint
│       ├── languages.py # Languages endpoint
│       └── ...
├── tests/
├── README.md
└── pyproject.toml
```

## Development

### Running tests

```bash
uv run pytest
```

With verbose output:

```bash
uv run pytest -v
```

### Adding dependencies

```bash
uv add <package-name>
```

### Adding dev dependencies

```bash
uv add --dev <package-name>
```

## Model Information

### NLLB-200

[NLLB-200-Distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M) from Meta AI.

- **Model size**: ~2.5GB
- **Supported languages**: 200+ languages
- **Architecture**: Encoder-Decoder Transformer
- **Language codes**: BCP-47 style (e.g., `eng_Latn`, `fra_Latn`)

### TranslateGemma

[TranslateGemma-4b-it](https://huggingface.co/google/translategemma-4b-it) from Google.

- **Model size**: ~8GB
- **Supported languages**: 55 languages
- **Architecture**: Gemma 3 based multimodal model
- **Language codes**: ISO 639-1 (e.g., `en`, `fr`, `de-DE`)
- **License**: Requires accepting Gemma license on Hugging Face

# Babelo

Offline neural machine translation between 200+ languages using Meta's NLLB-200 model with local-only, on-device inference.

## Features

- **200+ Languages**: Support for major and low-resource languages
- **Privacy-First**: Local translation inference
- **Text-to-Speech**: Listen to translations in supported languages in the browser
- **Translation History**: Save and revisit your translations
- **CLI & Web Interface**: Use via terminal or web app
- **Fast & Efficient**: Distilled 600M parameter model for speed

## Tech Stack

- **Backend**: Python, FastAPI, HuggingFace Transformers
- **Frontend**: React, TypeScript, Tailwind CSS
- **Model**: Facebook NLLB-200-distilled-600M

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Python package installer and resolver
- ~3GB disk space for the translation model

## Setup

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Download the translation model (~2.5GB):

   ```bash
   uv run bab download
   ```

   This downloads the `facebook/nllb-200-distilled-600M` model to `~/.cache/bab/models/`.

3. Verify the model files:

   ```bash
   uv run bab verify
   ```

4. Run the development server:

   ```bash
   uv run fastapi dev server/main.py
   ```

   Or using uvicorn directly:

   ```bash
   uv run uvicorn server.main:app --reload
   ```

5. Open http://localhost:8000 in your browser to see the API.

## CLI Commands

The `bab` CLI provides commands for managing the translation model:

### Check model status

```bash
uv run bab status
```

Shows whether the model is downloaded and loaded, along with storage location and size.

### Download the model

```bash
uv run bab download
```

Downloads the NLLB model to the local cache. Use `--force` to re-download:

```bash
uv run bab download --force
```

### Verify model files

```bash
uv run bab verify
```

Checks that all required model files are present.

### Test model loading

```bash
uv run bab load-test
```

Loads the model into memory to verify it works correctly.

### Custom cache directory

All commands support a custom cache directory:

```bash
uv run bab --cache-dir /path/to/cache status
```

## API Documentation

Once the server is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
babelo/
├── cli/
├── core/
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       └── utils/
├── server/
│   └── routes/
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

This project uses the [NLLB-200-Distilled-600M](https://huggingface.co/facebook/nllb-200-distilled-600M) model from Meta AI.

- **Model size**: ~2.5GB
- **Supported languages**: 200+ languages
- **Architecture**: Encoder-Decoder Transformer

The model is downloaded once and cached locally for reuse. On first load, there may be a delay while the model is loaded into memory.

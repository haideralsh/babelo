# Bab API

A FastAPI backend service for neural machine translation using Meta's NLLB-200 model.

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
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
   uv run fastapi dev src/bab/main.py
   ```

   Or using uvicorn directly:
   ```bash
   uv run uvicorn bab.main:app --reload
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
bab/
├── pyproject.toml          # Project configuration and dependencies
├── README.md               # This file
├── src/
│   └── bab/
│       ├── __init__.py
│       ├── cli.py          # CLI for model management
│       ├── main.py         # FastAPI application entry point
│       └── model.py        # Model loading and management
└── tests/
    ├── __init__.py
    ├── test_main.py        # API tests
    └── test_model.py       # Model management tests
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
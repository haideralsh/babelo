# Bab Translation Frontend

A React-based web interface for the Bab translation service.

## Setup Instructions

### 1. Install Dependencies

```bash
cd src/web-frontend
pnpm install
```

(Or use `npm install` or `yarn install` if you prefer)

### 2. Start the Backend Server

Make sure the backend server is running first. From the project root:

```bash
# Make sure you're in the project root directory
cd /Users/haider/code/bab

# Run the FastAPI server (you may need to activate your Python virtual environment first)
uvicorn src.server.main:app --reload
```

The backend should start on `http://localhost:8000`

### 3. Start the Frontend Development Server

In a new terminal, from the web-frontend directory:

```bash
cd src/web-frontend
pnpm dev
```

The frontend will start on `http://localhost:5173` (Vite's default port)

## Usage

1. Open your browser to `http://localhost:5173`
2. Select your source and target languages from the dropdowns
3. Enter text in the left textarea
4. Click the "Translate" button
5. The translation will appear in the right textarea

## Features

- **Language Selection**: Choose from all supported languages via dropdown menus
- **Language Swap**: Click the ⇄ button to swap source and target languages
- **Real-time Translation**: Sends requests to the backend API for translation
- **Error Handling**: Displays helpful error messages if something goes wrong
- **Responsive Design**: Works on desktop and mobile devices

## API Configuration

The frontend is configured to connect to the backend at `http://localhost:8000`. If your backend is running on a different port, update the `API_BASE_URL` constant in `src/App.tsx`.

## Troubleshooting

- **"Failed to fetch languages"**: Make sure the backend server is running on port 8000
- **CORS errors**: The backend has been configured to allow requests from `localhost:5173` and `localhost:3000`
- **Translation fails**: Ensure the model has been downloaded on the backend using the `/model/download` endpoint

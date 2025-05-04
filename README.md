# CodeCriticAI

CodeCriticAI is an agentic, AI-powered code review desktop application. It provides automated code review, refactoring suggestions, and code quality feedback using modern AI models.

## Features

- Automated code review and refactoring suggestions
- UI with inline comments and code highlighting
- Electron + React + Vite frontend
- Flask (Python) backend with AI integration
- Cross-platform desktop packaging

## Architecture

- **frontend/**: Electron + React + Vite desktop client
- **backend/**: Flask API server with AI code review logic

## Demo

https://github.com/user-attachments/assets/3bce2cff-1716-44c3-a68e-3343131e10ba

## Quick Start

### Prerequisites

- Node.js (v18+)
- Python 3.12+
- npm (v9+)
- (Optional) Electron globally for advanced packaging

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ljkart/CodeCriticAI.git
   cd CodeCriticAI
   ```
2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```
3. Install backend dependencies`:
   ```bash
   cd backend
   uv install .
   cd ..
   ```

### Running Both Frontend & Backend

- cd back to CodeCriticAI project root
- run `npm install `
- and run `npm run dev`

This will start both the backend server and the Electron frontend.

## Folder Structure

- `frontend/` — Electron + React desktop client
- `backend/` — Flask API server
- `docs/` — Documentation, screenshots, demo videos

## License

MIT

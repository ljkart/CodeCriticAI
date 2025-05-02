# CodeCriticAI-Frontend

A modern Electron + React + Vite desktop app for agentic code review tool.

## Prerequisites

- Node.js (v18 or higher recommended)
- npm (v9 or higher recommended)
- (Optional) [Electron](https://www.electronjs.org/) globally for advanced packaging

## Setup

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## Development

To run the app in development mode (with hot reload for React and Electron):

```bash
npm run dev
```

- This will start both the Vite dev server (for React) and Electron in development mode.
- The app window should open automatically. If not, run:
  ```bash
  npm run dev:electron
  ```

## Production Build

To build the React app and transpile the Electron main process:

```bash
npm run build
```

- The output will be in the `dist/` directory.

## Packaging the Electron App

To create a distributable package for your OS:

- **For Mac:**
  ```bash
  npm run dist:mac
  ```
- **For Windows:**
  ```bash
  npm run dist:win
  ```
- **For Linux:**
  ```bash
  npm run dist:linux
  ```

The packaged app will be in the `dist/` or `release/` directory.

## Environment Variables

Create a `.env` file in the `frontend/` directory if you need to override defaults (e.g., API endpoints).

## Troubleshooting

- If you see errors about missing dependencies, run `npm install` again.
- If Electron does not launch, ensure you are using a compatible Node.js version.
- For authentication issues, ensure your backend is running and accessible at the configured API endpoint.

## Project Structure

- `src/` - React components, pages, and services
- `electron/` - Electron main process and preload scripts
- `public/` - Static assets
- `dist/` - Production build output

## License

MIT

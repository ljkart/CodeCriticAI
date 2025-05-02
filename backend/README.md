# CodeReviewAgent-Backend

A Flask-based backend service for automated code review and analysis.

## Features

- User authentication and authorization using JWT
- Code review history tracking and versioning
- Support for multiple programming languages
- Integration with AI services for code analysis
- RESTful API endpoints for code review operations

## Prerequisites

- Python 3.12 or higher
- PostgreSQL (optional, SQLite used by default)
- OpenAI API key for AI-powered code analysis

## Installation

1. Clone the repository
2. install uv

3. Install dependencies:

   ```bash
   cd backend
   uv install .
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   AI_API_KEY=your-openai-api-key
   AI_MODEL=gpt-3.5-turbo
   DATABASE_URL=sqlite:///app/site.db  # Or your PostgreSQL URL
   ```

## Database Setup

Initialize the database:

```bash
flask db upgrade
```

## Running the Application

For development:

```bash
python app/run_app.py
```

For production:

```bash
uv run -- python -m gunicorn -w 2 --reload -b "0.0.0.0:8000" "app:create_app()"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

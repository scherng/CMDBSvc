# CMDB Service

AI-powered Configuration Management Database (CMDB) backend service for data ingestion and processing.

## Overview

This service provides REST API endpoints for ingesting raw data and retrieving processed results. It features a modular pipeline architecture with AI-ready processing capabilities (currently in no-op mode for development).

## Features

- **Data Ingestion**: REST API endpoint for uploading raw data
- **Data Retrieval**: Fetch processed data by unique ID
- **Background Processing**: Asynchronous data processing pipeline
- **AI-Ready Architecture**: Configurable AI models (OpenAI, Anthropic) for future data processing
- **SQLite Database**: Local data persistence with SQLAlchemy ORM
- **FastAPI Framework**: Modern, fast web framework with automatic API documentation

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository
2. Navigate to the project directory
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Service

Option 1 - Using the runner script:
```bash
python run.py
```

Option 2 - Direct execution:
```bash
python app/main.py
```

The service will start on `http://127.0.0.1:8000`

## API Endpoints

### Base URL: `http://127.0.0.1:8000`

- **POST** `/api/v1/ingest` - Ingest raw data
- **GET** `/api/v1/ci/{id}` - Fetch processed data by ID
- **GET** `/health` - Health check endpoint
- **GET** `/docs` - Interactive API documentation (Swagger UI)

### Example Usage

**Ingest Data:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
        {
          "user_id": "u_110",
          "name": "Jane Doe",
          "email": "jane.d@example.com",
          "groups": ["Engineering", "Admins"],
          "apps": ["GitHub", "Slack", "Salesforce"],
          "mfa_enabled": true,
          "last_login": "2024-07-15T10:03:00Z",
          "status": "ACTIVE"
        },
        {
          "user_id": "u_235",
          "name": "Carlos S.",
          "email": "c.santos@example.com",
          "groups": ["HR"],
          "apps": ["Workday"],
          "mfa_enabled": false,
          "last_login": "2024-06-21T08:41:00Z",
          "status": "ACTIVE"
        }
      }'
```

**Fetch Data:**
```bash
curl "http://127.0.0.1:8000/api/v1/ci/{record_id}"
```

## Project Structure

```
cmdbSvc/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── ingest.py          # Data ingestion endpoint
│   │       └── data.py            # Data retrieval endpoints
│   ├── core/
│   │   ├── data_processor.py      # Main data processing class
│   │   ├── pipeline.py            # Processing pipeline
│   │   └── schemas.py             # Pydantic models
│   ├── config/
│   │   └── settings.py            # Application configuration
│   ├── db/
│   │   ├── session.py             # Database session management
│   │   ├── models.py              # SQLAlchemy models (deprecated)
│   │   └── local_data_storage.py  # Data storage implementation
│   └── main.py                    # FastAPI application
├── run.py                         # Application runner script
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (not in git)
├── .gitignore                    # Git ignore patterns
└── README.md                     # This file
```


### Database Reset

If you need to reset the database schema:
```bash
rm -f cmdb.db
python app/main.py  # Will recreate tables
```

### Adding AI Processing

The architecture is ready for AI integration. Update `app/core/data_processor.py` to implement actual processing logic using the configured AI models.
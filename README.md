# Text Annotation Backend

A FastAPI-based backend system for text annotation and labeling, designed to manage annotation data with SQLite database and provide comprehensive REST API endpoints.

## Features

- **Annotation Data Management**: Store and manage text with associated labels (no duplicates)
- **Label Management**: Manage label definitions with ID and label string
- **Data Import**: Import existing labeled data and new unlabeled text
- **Search & Filtering**: Advanced search with text queries and label filters
- **Statistics**: Comprehensive statistics and analytics
- **Bulk Operations**: Bulk labeling and text import
- **RESTful API**: Complete REST API with FastAPI and automatic documentation

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Pydantic**: Data validation using Python type annotations
- **UV**: Fast Python package installer and resolver

## Project Structure

```
text-annotation/
├── main.py           # FastAPI application with all endpoints
├── models.py         # SQLAlchemy database models
├── schemas.py        # Pydantic schemas for API validation
├── services.py       # Business logic layer
├── data_import.py    # Data import utilities
├── run_import.py     # Script to import old data
├── README.md         # This file
└── pyproject.toml    # Project configuration and dependencies
```

## Installation & Setup

### Prerequisites

- Python 3.12+
- UV package manager

### Setup

1. **Clone and setup the project** (already done):
   ```bash
   cd text-annotation
   ```

2. **Install dependencies** (already done):
   ```bash
   uv sync
   ```

3. **Import existing data**:
   ```bash
   uv run python run_import.py
   ```

4. **Start the server**:
   ```bash
   uv run python main.py
   ```

   The API will be available at `http://localhost:8000`

5. **Access API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Database Schema

### AnnotationData Table
- `id`: Primary key (auto-generated)
- `text`: Text content (unique, no duplicates)
- `labels`: Comma-separated labels string

### Labels Table
- `id`: Unique identifier for the label
- `label`: The label string (unique)

## API Endpoints

### Health Check
- `GET /health` - Health check endpoint

### Annotation Data Management
- `POST /annotations/` - Create new annotation
- `GET /annotations/{id}` - Get annotation by ID
- `PUT /annotations/{id}` - Update annotation
- `DELETE /annotations/{id}` - Delete annotation
- `POST /annotations/search` - Search and filter annotations
- `POST /annotations/bulk-label` - Bulk label multiple texts
- `POST /annotations/import-texts` - Import multiple texts

### Label Management
- `POST /labels/` - Create new label
- `GET /labels/` - Get all labels
- `GET /labels/{id}` - Get label by ID
- `DELETE /labels/{id}` - Delete label

### Data Import
- `POST /import/old-data` - Import old labeled data
- `POST /import/label-config` - Import label configuration
- `POST /import/text-file` - Import text file

### Statistics
- `GET /stats/system` - Get system statistics

## Usage Examples

### 1. Search for annotations

```bash
curl -X POST "http://localhost:8000/annotations/search" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "product",
       "page": 1,
       "per_page": 10
     }'
```

### 2. Create a new annotation

```bash
curl -X POST "http://localhost:8000/annotations/" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "This is a sample text",
       "labels": "product,question"
     }'
```

### 3. Get unlabeled texts only

```bash
curl -X POST "http://localhost:8000/annotations/search" \
     -H "Content-Type: application/json" \
     -d '{
       "unlabeled_only": true,
       "page": 1,
       "per_page": 50
     }'
```

### 4. Bulk label multiple texts

```bash
curl -X POST "http://localhost:8000/annotations/bulk-label" \
     -H "Content-Type: application/json" \
     -d '{
       "text_ids": [1, 2, 3],
       "labels": "product,inquiry"
     }'
```

### 5. Get system statistics

```bash
curl -X GET "http://localhost:8000/stats/system"
```

### 6. Import new texts

```bash
curl -X POST "http://localhost:8000/annotations/import-texts" \
     -H "Content-Type: application/json" \
     -d '{
       "texts": [
         "New text to be labeled",
         "Another text for annotation"
       ]
     }'
```

## Data Import Process

The system handles two types of data import:

### 1. Old Labeled Data
- Located in `../old-data/**/*.txt` structure
- Each file represents a label, with each line being a text record
- Duplicate texts across files are merged with comma-separated labels
- Example: `old-data/product/askStock.txt` → texts get labeled as "askStock"

### 2. New Unlabeled Data
- Line-separated text files
- Each line becomes a new annotation record without labels
- Can be imported via API or file upload

## Development

### Running in Development Mode

```bash
# Start the server with auto-reload
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Operations

The SQLite database is created automatically at `annotation.db`. You can inspect it using any SQLite client:

```bash
sqlite3 annotation.db
.tables
.schema annotation_data
.schema labels
```

### Adding New Features

1. **Models**: Add new tables in `models.py`
2. **Schemas**: Add validation schemas in `schemas.py`
3. **Services**: Add business logic in `services.py`
4. **Endpoints**: Add API endpoints in `main.py`

## Configuration

### Environment Variables
- `DATABASE_URL`: SQLite database URL (default: `sqlite:///./annotation.db`)

### CORS Settings
Currently configured for development (`allow_origins=["*"]`). For production, configure specific origins.

## Production Deployment

For production deployment:

1. **Update CORS settings** in `main.py`
2. **Configure proper database** (PostgreSQL recommended for production)
3. **Add authentication** and authorization
4. **Set up proper logging**
5. **Use a production ASGI server** like Gunicorn with Uvicorn workers

```bash
# Example production command
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## License

This project is part of a text annotation system for managing labeled datasets.

# CMDB Service

A Configuration Management Database (CMDB) service built with FastAPI that provides entity management and AI-powered natural language querying capabilities.

## Architecture Overview

The CMDB service is designed with a modular architecture that supports multiple database backends, AI-enhanced field mapping, and natural language query processing.

### Core Components

```mermaid
classDiagram
    class DatabaseInterface {
        <<abstract>>
        +find_all(skip, limit)
        +find_by_id(id)
        +create(entity)
        +update(id, data)
        +delete(id)
        +close()
    }

    class MongoDBConnector {
        -client: MongoClient
        -database: Database
        +find_all(skip, limit)
        +find_by_id(id)
        +create(entity)
        +update(id, data)
        +delete(id)
        +close()
    }

    class InMemoryConnector {
        -data: Dict
        +find_all(skip, limit)
        +find_by_id(id)
        +create(entity)
        +update(id, data)
        +delete(id)
        +close()
    }

    class DatabaseFactory {
        +create_database(db_type) DatabaseInterface
    }

    DatabaseInterface <|-- MongoDBConnector
    DatabaseInterface <|-- InMemoryConnector
    DatabaseFactory --> DatabaseInterface
```

### Entity Models

```mermaid
classDiagram
    class EntityType {
        <<enumeration>>
        USER
        APPLICATION
        DEVICE
    }

    class UserBase {
        +name: str
        +team: Optional[str]
        +permission_group: List[str]
        +mfa_enabled: bool
        +last_login: Optional[datetime]
        +assigned_application_ids: List[str]
    }

    class User {
        +ci_id: str
        +user_id: str
        +create_new(**data) User
        +to_mongo() Dict
        +from_mongo(data) User
    }

    class ApplicationBase {
        +name: str
        +owner: str
        +type: ApplicationType
        +integrations: List[str]
        +usage_count: int
    }

    class Application {
        +ci_id: str
        +app_id: str
        +create_new(**data) Application
        +to_mongo() Dict
        +from_mongo(data) Application
    }

    class DeviceBase {
        +hostname: str
        +ip_address: str
        +os: OS
        +assigned_user: str
        +location: str
        +status: DeviceStatus
    }

    class Device {
        +ci_id: str
        +device_id: str
        +create_new(**data) Device
        +to_mongo() Dict
        +from_mongo(data) Device
    }

    UserBase <|-- User
    ApplicationBase <|-- Application
    DeviceBase <|-- Device
```

### Data Processing Pipeline

```mermaid
classDiagram
    class IngestionPipeline {
        -field_normalizer: FieldNormalizer
        -entity_parser: EntityParser
        +process(data_list) List[ProcessingResult]
        -_process_single_item(data) ProcessingResult
    }

    class FieldNormalizer {
        -llm_service: LLMService
        +normalize(data, entity_type) Dict
        -_llm_detect_entity_type(data) str
        -_get_llm_field_mappings(fields, entity_type) List[FieldMapping]
        -_apply_mappings(data, mappings) Dict
    }

    class EntityParser {
        +parse(entity_type, data) User|Application|Device
        -_create_user(data) User
        -_create_application(data) Application
        -_create_device(data) Device
    }

    class LLMService {
        <<singleton>>
        -_instance: LLMService
        -_llm: LLM
        +get_llm() LLM
        -_initialize()
    }

    IngestionPipeline --> FieldNormalizer
    IngestionPipeline --> EntityParser
    FieldNormalizer --> LLMService
```

### Query Engine

```mermaid
classDiagram
    class LLMToDbQueryHandler {
        -query_engine: SimpleLLMQuery
        -query_router: QueryRouter
        +prompt(prompt) Dict
        +execute_mongo_query(query) Dict
    }

    class SimpleLLMQuery {
        -index: VectorStoreIndex
        -jsonObj: str
        +custom_query(query_str) ChatResponse
    }

    class QueryRouter {
        -database: DatabaseInterface
        +execute(mongo_query) Dict
        -_execute_simple_query(query) Dict
        -_execute_aggregation(query) Dict
    }

    LLMToDbQueryHandler --> SimpleLLMQuery
    LLMToDbQueryHandler --> QueryRouter
    QueryRouter --> DatabaseInterface
```

## Features

### 1. Multi-Database Support
- **MongoDB**: Production database with full MongoDB query support
- **In-Memory**: Dictionary-based storage for testing and development
- **Database Factory**: Centralized database connector creation
- **Cursor Pattern**: Database-agnostic pagination

### 2. AI-Enhanced Data Processing
- **Field Mapping**: Automatically maps field variations to canonical names
  - Example: `mfa_status` → `mfa_enabled`, `group` → `team`
- **Entity Type Detection**: AI-powered detection of entity types from data
- **Confidence Scoring**: Provides confidence levels for mappings

### 3. Natural Language Querying
- **LLM Integration**: Converts natural language to MongoDB queries
- **Schema-Aware**: Uses enhanced schema for accurate query generation
- **Query Execution**: Executes generated queries and returns results

### 4. RESTful API
- **Entity Management**: CRUD operations for users, applications, and devices
- **Batch Processing**: Handle mixed entity types in single requests
- **Pagination**: Efficient pagination with skip/limit parameters
- **Natural Language Endpoint**: `/ask/` for natural language queries

## Assumptions & Limitations
- For this implementation, the data extraction and normalization are done in process synchronously. Though the data pipeline would be a perfect use case for streaming pipeline
- All data are immutable, no update and delete are allowed
    - this is mostly for simplicity purposes. But also to not spend too much time in the developing queries revision for MongoDB.
    - if Update is needed, then it will be done as part of the ingestion, and we would need to store the origination id (right now omitted after normalization) to compare the data.
- The ci_id is normalized throughout collections, no information of the CI entity type is exposed from the id.
- Assumptions on Dependency Mappings
- The natural language prompt can only work on a single collection at a time

## API Endpoints

### Data Endpoints
- `GET /api/v1/data/ci/{ci_id}` - Get entity by CI ID
- `GET /api/v1/data/users` - List all users (with pagination)
- `GET /api/v1/data/apps` - List all applications (with pagination)

### Ingestion Endpoints
- `POST /api/v1/ingest/` - Process and ingest entity data

### Query Endpoints
- `POST /ask/` - Natural language query interface

## Configuration

The service uses Pydantic settings for configuration:

```python
class Settings(BaseSettings):
    app_name: str = "CMDB Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database configuration
    database_type: str = "mongodb"  # Options: "mongodb", "memory"
    mongodb_url: str = "..."
    database_name: str = "cmdb_shm"

    # AI configuration
    openai_api_key: str = "..."
    enable_ai_field_mapping: bool = True
```

## Schema Management

The service includes automatic schema generation and updates:

- **Field Mapping Schema**: Defines canonical fields and variations for AI mapping
- **Enhanced DB Schema**: Provides LLM context for query generation
- **Auto-Update Script**: `update_schemas.py` synchronizes schemas with model changes

## Installation and Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables or `.env` file:
```bash
MONGODB_URL=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
DATABASE_TYPE=mongodb  # or "memory" for testing
```

3. Run the service:
```bash
python run.py
```

## Usage Examples

### Ingesting Data
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "full_name": "John Doe",
      "department": "Engineering",
      "mfa_status": true
    }
  ]'
```

### Natural Language Queries
```bash
curl -X POST "http://localhost:8000/ask/" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find all users in the Engineering team"}'
```

### Listing Entities
```bash
# Get all users
curl "http://localhost:8000/api/v1/data/users?skip=0&limit=50"

# Get all applications
curl "http://localhost:8000/api/v1/data/apps?skip=0&limit=50"
```

## Development

### Running Tests
The service supports both MongoDB and in-memory backends for testing:

```python
# Use in-memory database for tests
settings.database_type = "memory"
```

### Adding New Entity Types
1. Add enum value to `EntityType` in `models.py`
2. Create base and full model classes
3. Update field mapping schema
4. Add parser logic to `EntityParser`

### Extending Field Mappings
Add field variations to `field_mapping_schema.py`:

```python
"canonical_field": {
    "variations": ["variant1", "variant2", "variant3"],
    "type": "string",
    "required": True
}
```

## Architecture Benefits

- **Separation of Concerns**: Clear separation between data access, processing, and API layers
- **Testability**: In-memory database support for unit testing
- **Extensibility**: Easy to add new entity types and database backends
- **AI Integration**: Seamless integration of AI capabilities for data processing
- **Type Safety**: Strong typing with Pydantic models and enums
- **Performance**: Singleton LLM service prevents multiple initializations

## Project Structure

```
cmdbSvc/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       ├── ingest.py          # Data ingestion endpoint
│   │       └── data.py            # Data retrieval endpoints
│   ├── core/
│   │   ├── ingest/
│   │   │   ├── ingestion_pipeline.py # Main ingestion pipeline
│   │   │   ├── field_normalizer.py   # AI field mapping
│   │   │   └── entity_parser.py      # Entity creation
│   │   ├── prompt/
│   │   │   ├── llm_query_handler.py  # Natural language queries
│   │   │   └── query_router.py       # Query execution
│   │   ├── llm_data/
│   │   │   ├── db_enhanced_schema.py  # LLM schema context
│   │   │   └── field_mapping_schema.py # Field mapping definitions
│   │   ├── entity_data/
│   │   │   └── entity_manager.py     # Entity operations
│   │   ├── llm_service.py            # Singleton LLM service
│   │   └── schemas.py                # Pydantic models
│   ├── db/
│   │   ├── connection.py             # Database abstraction
│   │   ├── models.py                 # Entity models
│   │   └── repositories/             # Data access layer
│   ├── config/
│   │   └── settings.py               # Configuration
│   └── main.py                       # FastAPI application
├── update_schemas.py                 # Schema update utility
├── run.py                           # Application runner
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## Dependencies

- **FastAPI**: Web framework
- **Pydantic**: Data validation and settings
- **Motor**: Async MongoDB driver
- **LlamaIndex**: LLM integration framework
- **OpenAI**: AI model access

This CMDB service provides a robust, scalable, and AI-enhanced solution for configuration management with support for natural language querying and intelligent data processing.
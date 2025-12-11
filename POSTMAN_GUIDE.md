# MCP Server - Postman Testing Guide

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the HTTP wrapper server:
```bash
python http_wrapper.py
```

The server will start at `http://localhost:8000`

## Postman Requests

### 1. Health Check
**GET** `http://localhost:8000/`

Response:
```json
{
    "message": "MCP Server HTTP Wrapper is running",
    "status": "ok"
}
```

### 2. List All Tools
**GET** `http://localhost:8000/tools`

Response:
```json
{
    "tools": [...],
    "resources": [...]
}
```

### 3. Add Numbers Tool
**POST** `http://localhost:8000/tools/add_numbers`

Headers:
```
Content-Type: application/json
```

Body (raw JSON):
```json
{
    "a": 5,
    "b": 3
}
```

Response:
```json
{
    "result": 8,
    "status": "success"
}
```

### 4. Greet Tool
**POST** `http://localhost:8000/tools/greet`

Headers:
```
Content-Type: application/json
```

Body (raw JSON):
```json
{
    "name": "Varsha"
}
```

Response:
```json
{
    "result": "Hello, Varsha! Welcome to the MCP server.",
    "status": "success"
}
```

### 5. Get Info Tool
**GET** `http://localhost:8000/tools/get_info`

Response:
```json
{
    "result": {
        "server_name": "Demo MCP Server",
        "version": "1.0.0",
        "status": "running"
    },
    "status": "success"
}
```

### 6. Get Config Resource
**GET** `http://localhost:8000/resources/config`

Response:
```json
{
    "result": "Server configuration: Demo mode enabled",
    "status": "success"
}
```

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

You can test all endpoints directly from your browser using these interfaces!

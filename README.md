# Malagasy Customs AI Project

## Project Overview
This project is part of an initiative to develop generative AI solutions for Malagasy customs operations, focusing on task management and automation. This project is developed in collaboration with the International Monetary Fund (IMF) to enhance customs operations and digital transformation in Madagascar.

## Author Information
**Author:** Tojo Hasina RAJAONARIVO  
**Email:** besthorizon@outlook.com  
**Role:** AI Developer & Contributor  
**Contribution Period:** April 2025

## Project Description
This FastAPI-based application provides a RESTful API for task management, specifically designed for integration with Malagasy customs operations. The system implements basic CRUD operations for task management with a focus on scalability and maintainability. This project is part of a larger initiative supported by the IMF to modernize customs operations in Madagascar through AI and automation.

## Technical Stack
- FastAPI
- Pydantic
- Python

## API Endpoints
- `POST /tasks`: Create a new task
- `GET /tasks`: Retrieve all tasks

## License
This project is open source and available under the MIT License. See the LICENSE file for more details.

## Contact
For any inquiries regarding this project, please contact:
- Tojo Hasina RAJAONARIVO (besthorizon@outlook.com)
- IMF Technical Assistance Team

# Document Management API

A production-ready RESTful API for managing documents with deduplication support, built with FastAPI and SQLite.

## Features

- Upload documents (PDF, JPG, JPEG)
- Automatic deduplication based on SHA256 hash
- List all documents
- Search documents by BSC number and category
- Download documents
- File size formatting in Mo
- Page count for PDFs
- Production-ready configuration
- Environment variable support
- Security best practices

## Production Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```env
DATABASE_URL=sqlite:///./documents.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Document Management API
VERSION=1.0.0
```

4. Run the application with production settings:
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

For production deployment, consider using:
- Gunicorn as the WSGI server
- Nginx as a reverse proxy
- PostgreSQL instead of SQLite
- Proper SSL/TLS configuration
- Environment-specific settings

## API Endpoints

### Upload Document
```
POST /api/v1/documents/upload
```
Parameters:
- `bsc_number`: BSC number
- `category`: Document category
- `file`: Document file (PDF, JPG, JPEG)

### List Documents
```
GET /api/v1/documents/list
```

### Search Documents
```
GET /api/v1/documents/search
```
Query Parameters:
- `bsc_number`: Filter by BSC number
- `category`: Filter by category

### Download Document
```
GET /api/v1/documents/download/{doc_uuid}
```

## Project Structure

```
src/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services/
│   │   └── document_service.py
│   └── routers/
│       └── document_router.py
├── uploads/
├── .env
├── .gitignore
└── requirements.txt
```

## Security Considerations

1. Change the `SECRET_KEY` in production
2. Use HTTPS in production
3. Implement proper authentication
4. Set appropriate file upload limits
5. Validate all input data
6. Use environment variables for sensitive information
7. Implement rate limiting
8. Regular security audits

## Database

The application uses SQLite with SQLAlchemy ORM. For production, consider using PostgreSQL or another production-grade database.

## File Storage

Uploaded files are stored in the `uploads` directory, organized by document UUID. The original files are stored with their original names and extensions. 
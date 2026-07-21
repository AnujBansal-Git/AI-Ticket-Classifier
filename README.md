# AI Ticket Classifier

An AI-powered customer support ticket classification backend built with FastAPI, Scikit-learn, PostgreSQL, Celery, Redis, SQLAlchemy, Alembic, and Docker.

The application accepts individual support tickets and bulk CSV uploads, automatically classifies tickets using trained machine-learning models, predicts priority and the appropriate support team, generates summaries, performs sentiment analysis, and stores results in PostgreSQL.

Tickets that do not contain enough information for reliable automatic classification are stored separately for manual review. Reviewed classifications are stored as training feedback and are intended to support future model retraining.

Bulk classification is processed asynchronously using Celery and Redis so that large CSV operations do not block the FastAPI server.

---

## Features

- User registration and authentication
- JWT authentication using OAuth2 password flow
- Protected API endpoints
- Per-user data isolation
- Single-ticket classification
- Bulk ticket classification using CSV uploads
- Category prediction
- Priority prediction
- Automatic support-team routing
- Ticket summarization
- Sentiment analysis
- Classification validation for vague or insufficient tickets
- Rule-based prediction post-processing
- Storage of unclassified tickets
- Single-ticket manual review
- Bulk manual review
- Training-feedback collection
- Asynchronous background processing using Celery
- Redis message broker
- PostgreSQL persistent database
- SQLAlchemy ORM
- Alembic database migrations
- User-specific aggregate reports
- Authentication rate limiting
- Request logging with request IDs
- Centralized application error handling
- Dockerized deployment
- PostgreSQL and Redis health checks
- Dependency-aware container startup
- Non-root application containers
- Automated testing with pytest
- Test coverage reporting with pytest-cov
- Interactive Swagger and ReDoc documentation

---

## System Architecture

The application consists of four primary runtime services:

```text
                         Client / Swagger UI
                                |
                                v
                         +--------------+
                         | FastAPI API  |
                         +--------------+
                           |          |
                           |          |
                           v          v
                    +------------+  +-------+
                    | PostgreSQL |  | Redis |
                    +------------+  +-------+
                                       |
                                       v
                                +---------------+
                                | Celery Worker |
                                +---------------+
                                       |
                                       v
                              Classification Pipeline
                                       |
                                       v
                                  PostgreSQL
```

### FastAPI API

FastAPI provides HTTP endpoints for:

- authentication
- single-ticket classification
- classified-ticket retrieval
- bulk CSV processing
- bulk-job status and results retrieval
- manual review
- reporting

FastAPI automatically exposes interactive API documentation through Swagger UI and ReDoc.

### PostgreSQL

PostgreSQL is the application's persistent runtime database.

It stores data including:

- users
- classified tickets
- unclassified tickets
- bulk jobs
- training feedback

SQLAlchemy provides ORM-based database access.

Alembic manages database schema migrations.

### Redis

Redis is used as the Celery message broker and result backend.

When a bulk CSV file is submitted, the API creates a bulk-job record and queues a Celery task through Redis instead of processing the entire CSV synchronously.

### Celery Worker

The Celery worker receives queued bulk-processing tasks.

It processes tickets in the background and stores classification results in PostgreSQL.

This prevents long-running bulk classification operations from blocking normal API requests.

### Machine-Learning Layer

The ML layer handles runtime predictions for:

- category
- priority
- suggested support team

Additional application services provide:

- classification validation
- prediction post-processing
- summarization
- sentiment analysis
- manual review
- feedback collection

---

## Application Workflows

### Single-Ticket Classification

```text
Authenticated User
       |
       v
POST /tickets/classify
       |
       v
Classification Validation
       |
       +---------------------------+
       |                           |
       | Classifiable              | Insufficient Information
       v                           v
ML Predictions              Unclassified Ticket
       |                           |
       v                           v
Summary                    Manual Review Later
Sentiment                         |
Post-processing                   v
       |                    Training Feedback
       v
Classified Ticket
       |
       v
PostgreSQL
```

The workflow is:

1. An authenticated user submits ticket text.
2. The application checks whether the ticket contains enough information for automatic classification.
3. If the ticket is classifiable, the ML pipeline generates predictions.
4. The application generates a summary.
5. Sentiment analysis is performed.
6. Post-processing rules refine the results where applicable.
7. The classified ticket is stored in PostgreSQL under the authenticated user's ID.

If the ticket does not contain enough information, it is stored as an unclassified ticket instead of receiving a forced prediction.

The user can later provide a manual classification.

---

### Bulk-Ticket Classification

```text
Authenticated User
       |
       v
Upload CSV
       |
       v
POST /bulk-jobs
       |
       v
Validate File and CSV
       |
       v
Create BulkJob Record
       |
       v
Queue Celery Task
       |
       v
Redis
       |
       v
Celery Worker
       |
       v
Process Each Ticket
     /          \
    v            v
Classified    Unclassified
    |            |
    +----- PostgreSQL
```

The workflow is:

1. An authenticated user uploads a CSV file.
2. The API validates the file type and structure.
3. A bulk-job record is created.
4. The ticket data is submitted to Celery.
5. Redis transports the task to the worker.
6. The Celery worker processes the tickets.
7. Classified tickets are stored in PostgreSQL.
8. Tickets that cannot be automatically classified are stored separately.
9. Bulk-job counters and status are updated.
10. The client retrieves the results using the bulk-job endpoints.

This design allows the API to immediately return a job ID instead of waiting for the entire CSV to finish processing.

---

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic

### Database

- PostgreSQL
- SQLAlchemy
- Psycopg
- Alembic

### Machine Learning and NLP

- Scikit-learn
- Pandas
- NumPy
- Joblib
- Transformers
- PyTorch
- SentencePiece
- VADER Sentiment

### Authentication and Security

- JWT
- OAuth2 password flow
- python-jose
- Passlib
- bcrypt
- SlowAPI

### Background Processing

- Celery
- Redis

### Testing

- pytest
- pytest-cov
- FastAPI TestClient

### Deployment

- Docker
- Docker Compose

---

## Machine Learning Design

The project uses supervised machine-learning models trained using previously classified customer-support ticket data.

### Model Selection

Model experimentation and selection are considered internal R&D responsibilities.

The end user does not:

- choose a machine-learning algorithm
- compare candidate algorithms
- select the best model
- trigger model training through the public API

Candidate models can be benchmarked and evaluated during internal development.

The selected trained models are then loaded by the backend and used by the runtime prediction pipeline.

This separates two concerns:

```text
Internal ML Development
        |
        v
Training / Benchmarking / Evaluation
        |
        v
Selected Trained Model
        |
        v
Runtime API Prediction
```

The API consumer only interacts with the deployed classification system.

---

## Runtime Prediction

For an accepted ticket, the backend generates:

- category
- priority
- suggested support team

The classification is further enriched with:

- summary
- sentiment
- post-processing rules

This creates the final stored ticket record.

---

## Feedback and Retraining

When the automatic system cannot classify a ticket, the ticket is stored for manual review.

A reviewer provides the correct:

- category
- priority
- support team

The corrected classification is stored as training feedback.

The intended retraining workflow is:

```text
Existing Training Dataset
        +
Reviewed / Corrected Tickets
        |
        v
Updated Training Dataset
        |
        v
Internal Backend Retraining
        |
        v
Updated Trained Model
```

Retraining is intentionally an internal backend operation.

There is no public endpoint that allows an API user to directly train or retrain the machine-learning model.

Users contribute corrected classification data through the manual-review workflow, while model retraining remains an implementation and maintenance responsibility.

---

## Classification Labels

Manual review accepts predefined values.

### Category

```text
Incident
Problem
Request
Change
Feedback
```

### Priority

```text
low
medium
high
```

### Suggested Team

```text
Billing and Payments
Customer Service
General Inquiry
Human Resources
IT Support
Product Support
Returns and Exchanges
Sales and Pre-Sales
Service Outages and Maintenance
Technical Support
```

Category and suggested team represent different concepts.

For example:

```text
Category: Incident
Suggested Team: IT Support
```

---

## Project Structure

```text
AI Ticket Classifier/
|
├── alembic/
│   └── versions/                 # Database migration revisions
|
├── app/
│   ├── api/                      # API router modules
│   |
│   ├── auth/
│   │   ├── dependencies.py       # JWT/current-user dependencies
│   │   └── jwt_handler.py        # JWT handling
│   |
│   ├── core/
│   │   ├── limiter.py            # Rate limiter
│   │   └── logging.py            # Logging configuration
│   |
│   ├── db/
│   │   ├── database.py           # Database engine and Base
│   │   └── session.py            # Database sessions
│   |
│   ├── exceptions/
│   │   ├── custom_exceptions.py
│   │   └── handlers.py
│   |
│   ├── middleware/
│   │   └── request_logging.py
│   |
│   ├── ml/
│   │   ├── analyze_dataset.py
│   │   ├── benchmark.py
│   │   ├── check_dataset.py
│   │   ├── data_loader.py
│   │   ├── error_analysis.py
│   │   ├── evaluate_model.py
│   │   ├── model_io.py
│   │   ├── predict.py
│   │   ├── preprocessing.py
│   │   ├── retrain.py
│   │   ├── train.py
│   │   └── trainer.py
│   |
│   ├── models/
│   │   ├── user.py
│   │   ├── ticket.py
│   │   ├── unclassified_ticket.py
│   │   ├── bulk_job.py
│   │   └── training_feedback.py
│   |
│   ├── routes/
│   │   ├── auth.py
│   │   └── reports.py
│   |
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── ticket.py
│   │   ├── bulk_job.py
│   │   ├── review.py
│   │   └── unclassified_ticket.py
│   |
│   ├── services/
│   │   ├── auth.py
│   │   ├── bulk_job_service.py
│   │   ├── classification_validator.py
│   │   ├── post_processor.py
│   │   ├── review_service.py
│   │   ├── sentiment.py
│   │   └── summary.py
│   |
│   ├── celery_app.py
│   ├── tasks.py
│   └── main.py
|
├── models/                       # Serialized ML model files
├── reports/                      # ML reports/evaluation outputs
├── sample_data/                  # Sample datasets
├── tests/                        # Automated tests
|
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Prerequisites

### Recommended Method: Docker

Install:

- Docker
- Docker Compose

Docker is the recommended way to run the complete application because it automatically provides:

- FastAPI
- PostgreSQL
- Redis
- Celery worker

in a consistent environment.

### Local Development

For non-Docker execution, install:

- Python 3.12
- PostgreSQL
- Redis
- pip

---

## Environment Configuration

The application uses environment variables defined in a `.env` file.

Example:

```env
DATABASE_URL=postgresql+psycopg://ticket_user:ticket_password@postgres:5432/ticket_classifier
REDIS_URL=redis://redis:6379/0
SECRET_KEY=replace-with-a-secure-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

The Docker PostgreSQL configuration uses:

```text
Database: ticket_classifier
Username: ticket_user
Password: ticket_password
Host: postgres
Port: 5432
```

Redis is available inside the Docker Compose network at:

```text
redis://redis:6379/0
```

The `.env` file is excluded through `.gitignore` and should not be committed to source control.

For production or shared deployments:

- replace the example JWT secret
- use secure database credentials
- manage secrets through the deployment environment

---

## Running with Docker

Build and start the complete application:

```bash
docker compose up --build
```

This starts:

```text
ai-ticket-api
ai-ticket-worker
ai-ticket-postgres
ai-ticket-redis
```

The first build may take significant time because ML dependencies such as PyTorch and Transformers are large.

After the image has been built, normal startup can use:

```bash
docker compose up
```

### Access the Application

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Root health endpoint:

```text
http://localhost:8000/
```

### Service Startup

PostgreSQL and Redis have Docker health checks.

The API and worker wait for healthy dependencies before starting.

A successful Celery startup should show:

```text
Connected to redis://redis:6379/0
```

and:

```text
celery@... ready
```

The worker should also list:

```text
app.tasks.process_bulk_job_task
```

as a registered task.

---

## Running Locally Without Docker

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```text
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

When running outside Docker, change the database and Redis hostnames as necessary.

Docker service names such as:

```text
postgres
redis
```

normally cannot be resolved directly from the host operating system.

Start PostgreSQL and Redis, then start FastAPI:

```bash
uvicorn app.main:app --reload
```

Start the Celery worker in another terminal:

```bash
celery -A app.tasks worker --loglevel=info --concurrency=1
```

Open:

```text
http://localhost:8000/docs
```

---

## Database and Alembic Migrations

PostgreSQL provides persistent application storage.

SQLAlchemy defines the database models, while Alembic manages schema migrations.

### Check Current Migration

```bash
docker compose exec api alembic current
```

The database should report the current revision at `head` when all migrations are applied.

### Apply Migrations

```bash
docker compose exec api alembic upgrade head
```

### Check for Model/Database Differences

```bash
docker compose exec api alembic check
```

If the models and database schema are synchronized, Alembic should report:

```text
No new upgrade operations detected.
```

### Generate a Migration

After intentionally changing SQLAlchemy models:

```bash
docker compose exec api alembic revision --autogenerate -m "describe the schema change"
```

Review the generated migration before applying it.

Then run:

```bash
docker compose exec api alembic upgrade head
```

### Database Persistence

PostgreSQL data is stored in the Docker volume:

```text
postgres_data
```

Running:

```bash
docker compose down
```

does not delete this volume.

Therefore, data persists when containers are restarted.

Do not run:

```bash
docker compose down -v
```

unless you intentionally want to delete the PostgreSQL volume and its stored data.

---

## Authentication

The API uses JWT (JSON Web Token) authentication with the OAuth2 password flow.

Most application endpoints require an authenticated user.

### Authentication Flow

```text
Register User
     |
     v
POST /auth/register
     |
     v
Login
     |
     v
POST /auth/login
     |
     v
JWT Access Token
     |
     v
Authorization: Bearer <token>
     |
     v
Protected API Endpoints
```

### Using Authentication in Swagger UI

1. Open Swagger UI at `http://localhost:8000/docs`.
2. Use `POST /auth/register` to create a user.
3. Click the **Authorize** button in Swagger UI.
4. Enter the registered username and password.
5. Swagger sends the credentials to the login endpoint.
6. The returned JWT is automatically included when calling protected endpoints.

### Using Authentication Manually

First obtain an access token using:

```text
POST /auth/login
```

Then send the token with protected requests using the HTTP header:

```text
Authorization: Bearer <access_token>
```

If a protected endpoint is accessed without valid authentication, the API returns `401 Unauthorized`.

---

# API Reference

The following sections document the primary application endpoints.

Interactive documentation is also available through:

```text
Swagger UI: http://localhost:8000/docs
ReDoc:      http://localhost:8000/redoc
```

---

## Health Check

### `GET /`

Checks whether the FastAPI application is running.

Authentication is not required.

### Example Response

```json
{
  "message": "AI Ticket Classifier API is running."
}
```

### Expected Status

```text
200 OK
```

---

# Authentication Endpoints

## Register User

### `POST /auth/register`

Creates a new user account.

Authentication is not required.

The endpoint is rate limited to:

```text
5 requests per minute
```

### Request Body

```json
{
  "username": "testuser",
  "password": "example-password"
}
```

Both `username` and `password` are required.

### Successful Response

```json
{
  "message": "User registered successfully.",
  "user_id": 1
}
```

### Duplicate Username

If the username already exists:

```json
{
  "detail": "Username already exists."
}
```

### Possible Status Codes

```text
200 - User registered successfully
400 - Username already exists
422 - Invalid or missing request data
429 - Rate limit exceeded
```

Passwords are hashed before being stored in the database.

---

## Login

### `POST /auth/login`

Authenticates an existing user and returns a JWT access token.

Authentication is not required.

The endpoint is rate limited to:

```text
5 requests per minute
```

This endpoint uses OAuth2 form data rather than JSON.

### Form Fields

```text
username
password
```

### Example Successful Response

```json
{
  "access_token": "<jwt-access-token>",
  "token_type": "bearer"
}
```

### Invalid Credentials

```json
{
  "detail": "Invalid username or password."
}
```

The same error is returned whether the username does not exist or the password is incorrect.

### Possible Status Codes

```text
200 - Login successful
401 - Invalid username or password
422 - Missing form data
429 - Rate limit exceeded
```

---

## Get Current User

### `GET /auth/me`

Returns information about the currently authenticated user.

Authentication is required.

### Example Response

```json
{
  "id": 1,
  "username": "testuser"
}
```

Without authentication:

```json
{
  "detail": "Not authenticated"
}
```

### Possible Status Codes

```text
200 - Current user returned
401 - Authentication missing or invalid
```

---

# Ticket Classification Endpoints

## Classify a Single Ticket

### `POST /tickets/classify`

Classifies one customer-support ticket.

Authentication is required.

### Request Body

```json
{
  "ticket": "My laptop screen is broken and the device will not turn on."
}
```

The `ticket` field contains the original support-ticket text.

The application first checks whether the ticket contains enough information for automatic classification.

Two outcomes are possible.

---

### Outcome 1: Classified Ticket

If the ticket contains sufficient information, the application:

1. Predicts the category.
2. Predicts the priority.
3. Predicts the suggested support team.
4. Generates a summary.
5. Performs sentiment analysis.
6. Applies post-processing rules.
7. Stores the result in PostgreSQL.

Example response:

```json
{
  "id": 4,
  "status": "classified",
  "message": "Ticket classified successfully.",
  "ticket": "...",
  "category": "...",
  "priority": "...",
  "suggested_team": "...",
  "summary": "...",
  "sentiment": "..."
}
```

The returned `id` can be used to retrieve the complete classification.

---

### Outcome 2: Unclassified Ticket

If the classification validator determines that the ticket does not contain enough information, the application does not force an automatic classification.

Example response:

```json
{
  "id": 2,
  "status": "unclassified",
  "message": "The ticket could not be classified. Please provide more details or classify it manually."
}
```

The ticket is stored in the unclassified-ticket table with:

```text
source = "single"
```

The user can later classify it manually using the review endpoint.

---

## Retrieve Classified Tickets

### `GET /tickets`

Returns classified tickets belonging to the authenticated user.

Authentication is required.

### Retrieve All User Tickets

Request:

```text
GET /tickets
```

Example response:

```json
[
  {
    "id": 4,
    "ticket": "My laptop screen is broken and the device will not turn on.",
    "category": "Incident",
    "priority": "high",
    "suggested_team": "IT Support",
    "summary": "Laptop screen is broken and the device will not turn on.",
    "sentiment": "negative"
  }
]
```

The exact classification values depend on the trained models and post-processing logic.

Tickets are returned for the authenticated user only.

---

### Retrieve a Specific Ticket

Use the optional `ticket_id` query parameter:

```text
GET /tickets?ticket_id=4
```

Example response:

```json
{
  "id": 4,
  "ticket": "My laptop screen is broken and the device will not turn on.",
  "category": "Incident",
  "priority": "high",
  "suggested_team": "IT Support",
  "summary": "Laptop screen is broken and the device will not turn on.",
  "sentiment": "negative"
}
```

If the ticket does not exist:

```json
{
  "detail": "Ticket not found."
}
```

The same result is returned if the requested ticket belongs to another user.

This prevents a user from accessing another user's ticket by guessing its database ID.

---

# Manual Review

## Review a Single Unclassified Ticket

### `POST /unclassified-tickets/{ticket_id}/review`

Manually classifies a previously unclassified ticket.

Authentication is required.

The ticket must belong to the authenticated user.

### Example Request

```json
{
  "category": "Incident",
  "priority": "high",
  "team": "IT Support"
}
```

### Allowed Category Values

```text
Incident
Problem
Request
Change
Feedback
```

### Allowed Priority Values

```text
low
medium
high
```

### Allowed Team Values

```text
Billing and Payments
Customer Service
General Inquiry
Human Resources
IT Support
Product Support
Returns and Exchanges
Sales and Pre-Sales
Service Outages and Maintenance
Technical Support
```

### Successful Response

```json
{
  "message": "Ticket reviewed successfully.",
  "ticket_id": 5
}
```

The review workflow converts the manually reviewed ticket into a classified ticket and supports collection of corrected classification data for the training-feedback workflow.

If the ticket does not exist or does not belong to the authenticated user:

```json
{
  "detail": "Unclassified ticket not found."
}
```

If an unsupported category, priority, or team is submitted, Pydantic request validation rejects the request with:

```text
422 Unprocessable Entity
```

---

# Bulk Processing

## Create a Bulk Classification Job

### `POST /bulk-jobs`

Uploads a CSV file and starts asynchronous ticket classification.

Authentication is required.

The request uses:

```text
multipart/form-data
```

with a file upload.

### Required File Format

The uploaded file must:

1. Have a filename ending in `.csv`.
2. Contain valid CSV data.
3. Include a column named exactly `ticket`.

### Example CSV

```csv
ticket
"My laptop will not turn on"
"I was charged twice for my subscription"
"I cannot log into my account"
"help"
```

### Successful Response

```json
{
  "bulk_job_id": 2,
  "message": "Bulk job created successfully. Processing has started in the background."
}
```

The API:

1. Reads and validates the CSV.
2. Creates a bulk-job database record.
3. Sends the ticket list to a Celery background task.
4. Immediately returns the bulk-job ID.

The client can then use the returned ID to monitor processing.

---

## Bulk Upload Validation Errors

### Invalid File Type

If a non-CSV file is uploaded, such as a PDF:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Please upload a CSV file."
  }
}
```

Error code:

```text
INVALID_FILE_TYPE
```

---

### Invalid CSV Data

If Pandas cannot read the uploaded CSV:

```text
Error code: INVALID_CSV
Message: The uploaded CSV file could not be read.
```

---

### Missing Ticket Column

If the CSV does not contain a column named exactly `ticket`:

```text
Error code: MISSING_TICKET_COLUMN
Message: CSV must contain a 'ticket' column.
```

---

# Bulk Job Status

## Retrieve Bulk Job

### `GET /bulk-jobs/{job_id}`

Returns the status, processing counters and result for a bulk job.

Authentication is required.

The bulk job must belong to the authenticated user.

### Example Response

```json
{
  "id": 2,
  "filename": "tickets.csv",
  "status": "completed",
  "total_tickets": 5,
  "processed_tickets": 5,
  "classified_tickets_count": 4,
  "unclassified_tickets_count": 1,
  "classified_tickets": [
    ...
  ],
  "unclassified_tickets": [
    ...
  ]
}
```

The counters allow the client to determine:

- how many tickets were submitted
- how many have been processed
- how many were classified
- how many require manual review

If the bulk job does not exist or belongs to another user:

```json
{
  "detail": "Bulk job not found."
}
```

---

# Bulk Manual Review

## Review Multiple Unclassified Tickets

### `POST /bulk-jobs/{job_id}/review`

Manually reviews multiple unclassified tickets associated with a bulk job.

Authentication is required.

### Example Request

```json
[
  {
    "ticket_id": 7,
    "category": "Request",
    "priority": "low",
    "team": "General Inquiry"
  },
  {
    "ticket_id": 8,
    "category": "Incident",
    "priority": "high",
    "team": "Technical Support"
  }
]
```

Each item must contain:

```text
ticket_id
category
priority
team
```

The same predefined category, priority, and team values used by the single-ticket review endpoint apply.

### Example Successful Response

```json
{
  "message": "2 ticket(s) reviewed successfully."
}
```

For every submitted item, the application verifies:

- the unclassified ticket ID
- the bulk-job ID
- the authenticated user ID

The current implementation skips submitted items that do not correspond to an eligible unclassified ticket for the current user and bulk job.

Therefore, if two items are submitted but only one is valid, the operation can return:

```json
{
  "message": "1 ticket(s) reviewed successfully."
}
```

An invalid item does not cause the complete bulk-review request to fail.

---

# Reports

## Category Summary Report

### `GET /reports/category-summary`

Returns aggregate information about classified tickets belonging to the authenticated user.

Authentication is required.

The report contains:

- total number of classified tickets
- category distribution
- priority distribution
- sentiment distribution

### Example Response

```json
{
  "total_tickets": 5,
  "categories": [
    {
      "category": "Incident",
      "count": 2
    },
    {
      "category": "Request",
      "count": 3
    }
  ],
  "priorities": [
    {
      "priority": "high",
      "count": 2
    },
    {
      "priority": "low",
      "count": 3
    }
  ],
  "sentiments": [
    {
      "sentiment": "negative",
      "count": 2
    },
    {
      "sentiment": "neutral",
      "count": 3
    }
  ]
}
```

All four report components are filtered by the authenticated user's ID:

```text
total_tickets
categories
priorities
sentiments
```

Therefore, one user's ticket statistics are not included in another user's report.

---

# Security and User Data Isolation

The application uses the authenticated user's identity when accessing user-owned resources.

Protected endpoint dependencies use the current authenticated user.

User ownership filtering applies to:

- classified-ticket retrieval
- individual ticket lookup
- single unclassified-ticket review
- bulk-job retrieval
- bulk classified-ticket retrieval
- bulk unclassified-ticket retrieval
- bulk manual review
- reports

For example, when retrieving a specific classified ticket, the query checks both:

```text
ticket ID
authenticated user ID
```

This means that knowing another ticket's numeric database ID is not sufficient to access it.

The same principle is applied to bulk jobs and manual review operations.

Passwords are stored as password hashes rather than plaintext.

JWT access tokens identify authenticated users through the token subject.

---

# Rate Limiting

The application uses SlowAPI for authentication rate limiting.

Current limits:

```text
POST /auth/register    5 requests per minute
POST /auth/login       5 requests per minute
```

When the limit is exceeded, a rate-limit response is returned.

An observed response is:

```json
{
  "error": "Rate limit exceeded: 5 per 1 minute"
}
```

Rate limiting helps prevent excessive repeated requests against authentication endpoints.

---

# Request Logging

The application includes HTTP request-logging middleware.

Each request is logged with information including:

```text
request_id
HTTP method
endpoint
status code
latency
```

Example:

```text
request_id=05d881bc-7ee1-482c-911b-69b93f2adc4d
method=GET
endpoint=/auth/me
status=200
latency=0.004s
```

Responses include:

```text
X-Request-ID
```

This allows a client request to be correlated with the corresponding server log entry.

### View API Logs

```bash
docker compose logs -f api
```

### View Worker Logs

```bash
docker compose logs -f worker
```

### View All Logs

```bash
docker compose logs -f
```

---

# Error Handling

The application provides centralized handling for custom application errors.

## Authentication Error

Example:

```json
{
  "detail": "Not authenticated"
}
```

## Invalid Credentials

```json
{
  "detail": "Invalid username or password."
}
```

## Ticket Not Found

```json
{
  "detail": "Ticket not found."
}
```

## Bulk Job Not Found

```json
{
  "detail": "Bulk job not found."
}
```

## Unclassified Ticket Not Found

```json
{
  "detail": "Unclassified ticket not found."
}
```

## CSV Errors

CSV-related application errors provide:

- a machine-readable error code
- a human-readable error message

Example:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Please upload a CSV file."
  }
}
```

## Request Validation

FastAPI and Pydantic return:

```text
422 Unprocessable Entity
```

when request data does not match the declared schema.

Examples include:

- missing required fields
- unsupported category values
- unsupported priority values
- unsupported team values

---

# Automated Testing

The project uses `pytest` for automated testing and `pytest-cov` for coverage measurement.

The primary automated test suite is located in:

```text
tests/
```

The `pytest.ini` configuration restricts normal test discovery to this directory:

```ini
[pytest]
testpaths = tests
```

This is important because the project also contains older or standalone `test_*.py` files inside application directories such as `app/ml/` and `app/services/`.

Those files are not part of the current primary automated test suite.

---

## Run the Complete Test Suite

From the project root:

```bash
pytest -v
```

At the latest verification point, the configured test suite contained four tests:

```text
tests/test_auth.py::test_register_requires_valid_data
tests/test_auth.py::test_get_me_requires_authentication
tests/test_bulk_jobs.py::test_bulk_job_requires_authentication
tests/test_health.py::test_root
```

All four tests passed:

```text
4 passed
```

The warnings currently displayed by pytest are dependency deprecation warnings and do not represent failed tests.

---

## Current Automated Tests

### Health Endpoint Test

```text
tests/test_health.py::test_root
```

Verifies that the root API endpoint is available and responds successfully.

This acts as a basic application smoke test.

---

### Registration Validation Test

```text
tests/test_auth.py::test_register_requires_valid_data
```

Verifies that the registration endpoint requires valid request data.

---

### Authentication Protection Test

```text
tests/test_auth.py::test_get_me_requires_authentication
```

Verifies that the current-user endpoint cannot be accessed without authentication.

Expected result:

```text
401 Unauthorized
```

---

### Bulk Authentication Test

```text
tests/test_bulk_jobs.py::test_bulk_job_requires_authentication
```

Verifies that bulk-job creation cannot be performed by an unauthenticated client.

Expected result:

```text
401 Unauthorized
```

---

# Test Coverage

Run coverage for the complete `app` package:

```bash
pytest --cov=app --cov-report=term-missing
```

The latest development measurement produced approximately:

```text
TOTAL COVERAGE: 41%
```

A more focused measurement of runtime/API-oriented modules can be executed with:

```bash
pytest \
  --cov=app.main \
  --cov=app.auth \
  --cov=app.routes \
  --cov=app.services \
  --cov-report=term-missing
```

The latest measured coverage for this selected module set was approximately:

```text
42%
```

These figures should not be interpreted as comprehensive production-level test coverage.

The project contains ML development modules for:

- dataset analysis
- dataset checking
- model training
- benchmarking
- evaluation
- error analysis
- retraining

These scripts are not all executed during normal API requests and therefore reduce whole-package coverage when included in the measurement.

The current automated test suite should be considered a basic smoke and security test suite.

The manual and end-to-end test cases below provide broader validation of the current application and identify suitable areas for future automated integration testing.

---

# Manual and End-to-End Test Cases

The following test matrix covers the main functional, security, asynchronous-processing, database, Docker, and operational requirements of the application.

| ID | Area | Test Case | Expected Result |
|---|---|---|---|
| TC-01 | Health | Call `GET /` | HTTP 200 and API-running message returned |
| TC-02 | Documentation | Open `/docs` | Swagger UI loads successfully |
| TC-03 | Documentation | Open `/redoc` | ReDoc documentation loads |
| TC-04 | Authentication | Register a new user with valid data | User created successfully |
| TC-05 | Authentication | Register an existing username | HTTP 400 and duplicate username rejected |
| TC-06 | Authentication | Register without required username/password | HTTP 422 |
| TC-07 | Authentication | Login using valid credentials | JWT access token returned |
| TC-08 | Authentication | Login using incorrect password | HTTP 401 |
| TC-09 | Authentication | Login using nonexistent username | HTTP 401 |
| TC-10 | Authentication | Call `/auth/me` without JWT | HTTP 401 |
| TC-11 | Authentication | Call `/auth/me` with valid JWT | Current user's ID and username returned |
| TC-12 | Rate Limiting | Exceed registration rate limit | Rate-limit response returned |
| TC-13 | Rate Limiting | Exceed login rate limit | Rate-limit response returned |
| TC-14 | Classification | Submit clear support ticket | Classified response and ticket ID returned |
| TC-15 | Classification | Retrieve all current-user tickets | Current user's classified tickets returned |
| TC-16 | Classification | Retrieve owned ticket using `ticket_id` | Correct ticket returned |
| TC-17 | Classification | Retrieve nonexistent ticket ID | HTTP 404 |
| TC-18 | User Isolation | User A requests User B's ticket ID | HTTP 404; User B's data not exposed |
| TC-19 | Classification Validation | Submit insufficient ticket such as `help` | Ticket stored/returned as unclassified |
| TC-20 | Manual Review | Review owned unclassified ticket with valid labels | Ticket reviewed successfully |
| TC-21 | Manual Review | Review nonexistent unclassified ticket | HTTP 404 |
| TC-22 | User Isolation | User A reviews User B's unclassified ticket | HTTP 404 |
| TC-23 | Review Validation | Submit unsupported category | HTTP 422 |
| TC-24 | Review Validation | Submit unsupported priority | HTTP 422 |
| TC-25 | Review Validation | Submit unsupported team | HTTP 422 |
| TC-26 | Bulk Upload | Upload valid CSV containing `ticket` column | Bulk job created |
| TC-27 | Bulk Upload | Upload PDF or another non-CSV file | `INVALID_FILE_TYPE` returned |
| TC-28 | Bulk Upload | Upload unreadable/invalid CSV | `INVALID_CSV` returned |
| TC-29 | Bulk Upload | Upload CSV without `ticket` column | `MISSING_TICKET_COLUMN` returned |
| TC-30 | Bulk Security | Create bulk job without authentication | HTTP 401 |
| TC-31 | Bulk Status | Retrieve owned bulk job | Job status and counters returned |
| TC-32 | Bulk Isolation | Retrieve nonexistent bulk job | HTTP 404 |
| TC-33 | Bulk Isolation | User A retrieves User B's bulk job | HTTP 404 |
| TC-34 | Celery | Submit valid bulk job | Worker receives `process_bulk_job_task` |
| TC-35 | Celery | Allow bulk processing to finish | Worker reports task succeeded |
| TC-36 | Bulk Results | Retrieve classified tickets for bulk job | Matching classified results returned |
| TC-37 | Bulk Results | Retrieve unclassified tickets for bulk job | Matching unclassified results returned |
| TC-38 | Bulk Isolation | User A queries User B's bulk classified results | User B's records are not returned |
| TC-39 | Bulk Isolation | User A queries User B's unclassified results | User B's records are not returned |
| TC-40 | Bulk Review | Review valid bulk unclassified tickets | Successful review count returned |
| TC-41 | Bulk Review | Include a nonmatching ticket ID | Invalid item skipped; eligible items processed |
| TC-42 | Bulk Review | Submit invalid category/priority/team | HTTP 422 |
| TC-43 | Reports | Call report without authentication | HTTP 401 |
| TC-44 | Reports | Call report with valid authentication | Report returned |
| TC-45 | Reports | Compare `total_tickets` with current user's records | Total matches authenticated user's classified tickets |
| TC-46 | Reports | Validate category counts | Counts match authenticated user's tickets |
| TC-47 | Reports | Validate priority counts | Counts match authenticated user's tickets |
| TC-48 | Reports | Validate sentiment counts | Counts match authenticated user's tickets |
| TC-49 | Report Isolation | Compare reports for two different users | Each user receives only their own statistics |
| TC-50 | Persistence | Create data, run `docker compose down`, then restart | PostgreSQL data remains available |
| TC-51 | Docker | Start complete Compose stack | All four services start |
| TC-52 | Docker Health | Observe PostgreSQL startup | PostgreSQL reaches healthy state |
| TC-53 | Docker Health | Observe Redis startup | Redis reaches healthy state |
| TC-54 | Docker Dependencies | Start application stack | API and worker wait for healthy dependencies |
| TC-55 | Worker | Inspect Celery startup | Worker connects to Redis |
| TC-56 | Worker | Inspect registered tasks | `app.tasks.process_bulk_job_task` is registered |
| TC-57 | Container Security | Inspect application container startup | Application runs using configured non-root user |
| TC-58 | Alembic | Run `alembic current` | Current database revision displayed |
| TC-59 | Alembic | Verify migration state | Revision is at expected `head` |
| TC-60 | Alembic | Run `alembic check` | No unexpected schema operations detected |
| TC-61 | Automated Tests | Run `pytest -v` | Configured test suite passes |
| TC-62 | Coverage | Run pytest with coverage | Coverage report generated |
| TC-63 | Logging | Make API request | Method, endpoint, status, latency and request ID logged |
| TC-64 | Logging | Inspect API response | `X-Request-ID` header is present |
| TC-65 | Error Handling | Trigger custom CSV error | Structured custom error response returned |

---

# Recommended Future Automated Tests

The existing four automated tests establish basic application availability and authentication protection.

For stronger regression protection, the following tests should be automated in future development.

### Authentication Integration Tests

Add tests for:

- successful registration
- duplicate username rejection
- successful login
- invalid login
- JWT-protected endpoint access
- invalid or expired JWT

### Ticket Integration Tests

Add tests for:

- successful ticket classification
- unclassified-ticket path
- retrieving all tickets
- retrieving a specific ticket
- cross-user ticket isolation

### Bulk Integration Tests

Add tests for:

- valid CSV upload
- invalid file type
- missing `ticket` column
- bulk-job ownership
- bulk-job completion
- classified result retrieval
- unclassified result retrieval

Celery can be configured for test execution using an eager testing mode or tested using an integration environment.

### Review Tests

Add tests for:

- valid manual review
- invalid category
- invalid priority
- invalid team
- cross-user review protection
- bulk review
- partial bulk review with skipped IDs

### Report Tests

Add tests that create records for multiple users and verify that:

```text
total_tickets
categories
priorities
sentiments
```

are all isolated by authenticated user ID.

### Database Tests

Tests should use an isolated test database or transaction rollback strategy so that automated tests do not modify development or production data.

---

# Verified End-to-End Workflow

During development, the primary runtime workflow was manually verified using the complete Docker stack.

The verified sequence was:

```text
docker compose up --build
        |
        v
PostgreSQL Starts
        |
        v
Redis Starts
        |
        v
PostgreSQL Healthy
Redis Healthy
        |
        v
FastAPI Starts
Celery Worker Starts
        |
        v
Swagger UI Opens
        |
        v
User Registration
        |
        v
User Login
        |
        v
JWT Authentication
        |
        v
GET /auth/me
        |
        v
Single Ticket Classification
        |
        v
GET /tickets
        |
        v
Bulk CSV Upload
        |
        v
Celery Task Queued
        |
        v
Worker Receives Task
        |
        v
Worker Processes Tickets
        |
        v
Task Completes Successfully
        |
        v
GET /bulk-jobs/{job_id}
        |
        v
Classified & Unclassified Results
        |
        v
Manual Review
```

---

# Verified Service Communication

The successful end-to-end workflow demonstrates communication between the major components.

### Client to FastAPI

```text
Client
  |
  v
FastAPI
```

Used for:

- registration
- authentication
- classification
- bulk uploads
- result retrieval
- manual review
- reports

### FastAPI to PostgreSQL

```text
FastAPI
  |
  v
PostgreSQL
```

Used for persistent application data.

### FastAPI to Redis to Celery

```text
FastAPI
  |
  v
Redis
  |
  v
Celery Worker
```

Used for asynchronous bulk-processing tasks.

### Celery to PostgreSQL

```text
Celery Worker
     |
     v
PostgreSQL
```

Used to persist background classification results and update bulk-job status.

The complete runtime architecture therefore operates as:

```text
Client
  |
  v
FastAPI <----------> PostgreSQL
  |
  v
Redis
  |
  v
Celery Worker -----> PostgreSQL
```

---

# Example Verified Runtime Logs

A successful API request produces logs similar to:

```text
method=POST endpoint=/auth/register status=200
method=POST endpoint=/auth/login status=200
method=GET endpoint=/auth/me status=200
method=POST endpoint=/tickets/classify status=200
method=GET endpoint=/tickets status=200
```

A successfully processed bulk task produces worker logs similar to:

```text
Task app.tasks.process_bulk_job_task[...] received
```

followed by:

```text
Task app.tasks.process_bulk_job_task[...] succeeded
```

The job can then be queried through:

```text
GET /bulk-jobs/{job_id}
```

and classified results through:

```text
GET /bulk-jobs/{job_id}/tickets
```

---

# Testing Notes

## Dependency Warnings

During pytest execution, warnings may be displayed from third-party dependencies.

Observed examples include:

```text
StarletteDeprecationWarning
```

related to the FastAPI/Starlette TestClient dependency stack, and:

```text
DeprecationWarning: 'crypt' is deprecated
```

originating from Passlib dependencies.

These warnings do not currently cause test failures.

They should be reviewed during future dependency upgrades.

---

## Difference Between Passing Tests and Full Verification

A passing automated test suite means that the behaviors covered by those tests are working.

It does not automatically prove that every application feature works.

For this reason, the project uses three complementary verification approaches:

```text
Automated Tests
      +
Manual API Testing
      +
Docker End-to-End Testing
```

Automated tests currently verify core smoke/security behavior.

Manual testing verifies the wider API feature set.

Docker end-to-end testing verifies that the complete multi-service architecture works together.

Future development should progressively convert important manual test cases into automated integration tests.

---

# Docker Operations

Docker Compose manages the complete application stack.

The services are:

```text
api
worker
postgres
redis
```

---

## Start the Application

If the Docker images already exist:

```bash
docker compose up
```

---

## Build and Start

Use this after changing:

- `Dockerfile`
- `requirements.txt`
- installed Python dependencies

Command:

```bash
docker compose up --build
```

The initial build can take significant time because the project contains large machine-learning dependencies.

---

## Stop the Application

```bash
docker compose down
```

This stops and removes the containers and network but preserves the PostgreSQL named volume.

---

## View Container Status

```bash
docker compose ps
```

Use this to check whether:

- API is running
- Celery worker is running
- PostgreSQL is healthy
- Redis is healthy

---

## View Logs

View all service logs:

```bash
docker compose logs
```

Follow logs continuously:

```bash
docker compose logs -f
```

API logs:

```bash
docker compose logs -f api
```

Celery worker logs:

```bash
docker compose logs -f worker
```

PostgreSQL logs:

```bash
docker compose logs -f postgres
```

Redis logs:

```bash
docker compose logs -f redis
```

---

## Restart a Service

Restart the API:

```bash
docker compose restart api
```

Restart the worker:

```bash
docker compose restart worker
```

---

## Execute Commands Inside the API Container

General format:

```bash
docker compose exec api <command>
```

Examples:

```bash
docker compose exec api alembic current
```

```bash
docker compose exec api alembic check
```

```bash
docker compose exec api alembic upgrade head
```

---

## Validate Docker Compose Configuration

Run:

```bash
docker compose config
```

This validates the Compose file and displays the final resolved configuration.

It is useful for detecting:

- YAML indentation problems
- invalid service definitions
- dependency configuration
- environment-variable values
- volume configuration

---

## Remove Containers Without Deleting Database Data

```bash
docker compose down
```

The PostgreSQL `postgres_data` volume remains available.

---

## Delete Containers and Database Data

Use only when a complete database reset is intentional:

```bash
docker compose down -v
```

This removes named Docker volumes.

Any PostgreSQL data stored in `postgres_data` will be deleted.

---

# Troubleshooting

## API Does Not Start

Check container status:

```bash
docker compose ps
```

Then inspect API logs:

```bash
docker compose logs -f api
```

Also verify that PostgreSQL and Redis are healthy.

The API depends on these services.

---

## PostgreSQL Does Not Become Healthy

Inspect PostgreSQL logs:

```bash
docker compose logs -f postgres
```

The configured health check uses PostgreSQL's `pg_isready`.

Verify that the following values are consistent between Docker Compose and the application configuration:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL
```

The current Docker configuration uses:

```text
User: ticket_user
Database: ticket_classifier
```

---

## PostgreSQL Connection Fails from the API

Inside Docker Compose, the PostgreSQL hostname is:

```text
postgres
```

Do not use:

```text
localhost
```

from one container to connect to another container.

The Docker database URL follows this pattern:

```text
postgresql+psycopg://ticket_user:ticket_password@postgres:5432/ticket_classifier
```

When the application is run directly on the host instead of inside Docker, configure a host-reachable database address such as `localhost` where appropriate.

---

## Redis Connection Fails

Inside Docker Compose, Redis is available using:

```text
redis://redis:6379/0
```

Verify that:

- the Redis container is running
- the Redis health check passes
- `REDIS_URL` uses the correct hostname
- the API and worker are on the same Docker Compose network

Check:

```bash
docker compose logs -f redis
```

---

## Celery Worker Does Not Start

Inspect worker logs:

```bash
docker compose logs -f worker
```

A successful startup should show a Redis connection and eventually:

```text
celery@... ready
```

The registered task list should include:

```text
app.tasks.process_bulk_job_task
```

---

## Bulk Job Is Created but Never Completes

Check the worker:

```bash
docker compose logs -f worker
```

After submitting a bulk job, the worker should log something similar to:

```text
Task app.tasks.process_bulk_job_task[...] received
```

and eventually:

```text
Task app.tasks.process_bulk_job_task[...] succeeded
```

If no task is received, verify the Redis connection.

If the task is received but fails, inspect the worker traceback and verify database connectivity.

---

## Redis Memory Overcommit Warning

Redis may display a warning similar to:

```text
WARNING Memory overcommit must be enabled!
```

This is a host-level Redis configuration warning.

It does not necessarily prevent the current local development environment from working.

For production Redis deployments, configure the host according to Redis deployment recommendations.

---

## Docker Build Takes a Long Time

The application contains large ML dependencies including:

- PyTorch
- Transformers

The first installation and image export can therefore take significant time.

Avoid unnecessary rebuilds.

If only application source code changed and the current development Compose configuration bind-mounts the repository into `/app`, a complete dependency rebuild may not be required.

Use:

```bash
docker compose up
```

instead of:

```bash
docker compose up --build
```

when dependencies and the Dockerfile have not changed.

---

## Source Code Changed but Behavior Did Not Update

The project currently bind-mounts the source directory:

```text
.:/app
```

Therefore, source files on the host are visible inside the application container.

However, the running Python process may still need to be restarted if Uvicorn is not running with automatic reload.

Restart the relevant service:

```bash
docker compose restart api
```

For Celery task changes:

```bash
docker compose restart worker
```

---

## CSV Upload Returns `INVALID_FILE_TYPE`

The bulk endpoint only accepts files whose filenames end with:

```text
.csv
```

A PDF, Excel file, image, or other file type is rejected.

Expected error code:

```text
INVALID_FILE_TYPE
```

---

## CSV Upload Returns `MISSING_TICKET_COLUMN`

The uploaded CSV must contain a column named exactly:

```text
ticket
```

Example:

```csv
ticket
"My laptop will not turn on"
"I cannot access my account"
```

Column naming is case-sensitive according to the current implementation.

---

## Authentication Returns 401

Verify that:

1. The user has been registered.
2. The correct username and password are being used.
3. A valid access token was obtained.
4. The token is included as a Bearer token.

Header format:

```text
Authorization: Bearer <access_token>
```

In Swagger UI, use the **Authorize** button.

---

## Authentication Returns 429

The registration and login endpoints are rate limited.

Current limits:

```text
5 requests per minute
```

Wait until the rate-limit window resets before trying again.

---

## Alembic Reports the Wrong Database

Verify:

```text
DATABASE_URL
```

When migrations run inside Docker, the PostgreSQL hostname should normally be:

```text
postgres
```

Run:

```bash
docker compose exec api alembic current
```

This ensures the migration command runs using the application container's environment.

---

## Alembic Detects Unexpected Schema Changes

Run:

```bash
docker compose exec api alembic check
```

If changes are detected, compare:

- SQLAlchemy models
- existing Alembic revisions
- current database schema

Do not automatically generate and apply migrations without reviewing the detected differences.

If the model change is intentional:

```bash
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Review the migration and then run:

```bash
docker compose exec api alembic upgrade head
```

---

## Database Data Disappeared

Normal shutdown:

```bash
docker compose down
```

preserves PostgreSQL data.

However:

```bash
docker compose down -v
```

deletes named volumes.

If `-v` was used, PostgreSQL data stored in the Docker volume may have been permanently removed.

---

## Pytest Tries to Run Old Tests from `app/`

Verify that `pytest.ini` contains:

```ini
[pytest]
testpaths = tests
```

Run pytest from the project root:

```bash
pytest -v
```

This limits the primary test suite to the dedicated `tests/` directory.

---

## Pytest Displays Deprecation Warnings

The current development environment may display warnings originating from third-party libraries.

Examples include:

```text
StarletteDeprecationWarning
```

and:

```text
DeprecationWarning: 'crypt' is deprecated
```

These warnings currently do not indicate failed application tests.

They should be addressed through dependency upgrades when compatible versions are available.

---

# Scope and Design Decisions

The following decisions define the intended responsibilities of the current system.

---

## 1. Model Selection Is an Internal R&D Process

Machine-learning model comparison is not exposed to the application user.

During development, candidate algorithms can be:

- trained
- benchmarked
- evaluated
- compared

The development process selects the model considered most appropriate for deployment.

The deployed API then uses the selected trained model.

The runtime user does not need to understand or select the underlying algorithm.

This separates:

```text
ML Research and Development
```

from:

```text
Runtime Application Usage
```

---

## 2. There Is No Public Model-Training Endpoint

The application intentionally does not expose an endpoint such as:

```text
POST /train
```

or:

```text
POST /retrain
```

Model training is considered an internal backend operation.

The public API focuses on:

- classification
- feedback collection
- review
- reporting

This prevents API consumers from directly modifying the deployed ML model.

---

## 3. Manual Review Provides Training Feedback

Tickets that cannot be automatically classified can be manually reviewed.

The reviewer provides the correct:

- category
- priority
- support team

The corrected classification can then be stored as training feedback.

This creates a feedback loop:

```text
Automatic Classification
        |
        v
Unclassified / Needs Review
        |
        v
Human Correction
        |
        v
Training Feedback
        |
        v
Future Internal Retraining
```

The user provides the corrected labels.

The backend development/retraining process determines when and how those labels are incorporated into future models.

---

## 4. Insufficient Tickets Are Not Forced Through the Model

A support request such as:

```text
help
```

may not contain enough information for a meaningful classification.

The application therefore includes classification validation before normal prediction.

If the ticket is considered insufficient:

```text
Ticket
  |
  v
Classification Validator
  |
  v
Unclassified Ticket Storage
  |
  v
Manual Review
```

This is preferable to generating a potentially misleading automatic classification.

---

## 5. Bulk Processing Is Asynchronous

Bulk CSV processing can take longer than a single API request.

The application therefore uses:

```text
FastAPI
   |
   v
Celery
   |
   v
Redis
```

for background execution.

The API returns a bulk-job ID immediately.

The client can then poll:

```text
GET /bulk-jobs/{job_id}
```

to retrieve status.

This prevents large CSV files from blocking the main API request lifecycle.

---

## 6. PostgreSQL Is the Current Runtime Database

The current application architecture uses PostgreSQL for persistent runtime storage.

Old local SQLite database files may still exist in a development directory, but they are not part of the intended current Docker runtime architecture.

The Dockerized application connects to PostgreSQL through the Compose service.

---

## 7. User-Owned Data Is Isolated

Authentication is not used only to identify who is logged in.

The authenticated user ID is also used to filter user-owned database records.

This applies to:

- classified tickets
- ticket lookup
- unclassified-ticket review
- bulk jobs
- bulk results
- bulk manual review
- reports

This prevents users from accessing another user's application data simply by knowing a database ID.

---

## 8. Reports Are User-Specific

The category-summary report calculates:

```text
total tickets
category counts
priority counts
sentiment counts
```

using the authenticated user's ID.

The report therefore represents the current user's ticket data rather than global application data.

---

## 9. Reporting and ML Evaluation Are Separate Concerns

The runtime report endpoint provides operational ticket statistics.

Internal ML evaluation scripts handle model-development concerns such as:

- benchmarking
- evaluation
- error analysis

These are separate responsibilities.

The current API does not expose internal model-development reports to runtime users.

---

## 10. Docker Provides Environment Consistency

A Python virtual environment isolates Python packages on one machine.

Docker provides broader isolation by packaging:

- Python runtime
- application dependencies
- application environment

Docker Compose additionally coordinates:

- FastAPI
- Celery
- PostgreSQL
- Redis

The virtual environment remains useful for local development and testing, while Docker provides a reproducible multi-service runtime environment.

---

# Current Limitations

The project implements the required core workflow but is not intended to represent a fully hardened enterprise production deployment.

Current limitations include:

- Automated test coverage is still limited.
- Many end-to-end scenarios are manually verified rather than automated.
- Ticket-list endpoints do not currently provide pagination.
- Bulk upload size and row-count limits could be made more explicit.
- Production-grade secret management is not included.
- JWT refresh/revocation workflows are not implemented.
- Production monitoring and alerting are not included.
- Distributed tracing is not implemented.
- ML drift monitoring is not automated.
- Model retraining remains an internal/manual backend process.
- Sentiment and summarization quality depend on the current NLP implementations and models.

---

# Future Improvements

Possible future improvements include:

- Expand automated integration tests.
- Increase test coverage for classification logic.
- Add automated cross-user security tests.
- Add automated Celery integration tests.
- Add report-isolation tests.
- Add database test fixtures and transaction rollback.
- Add pagination to ticket retrieval.
- Add pagination to bulk-result retrieval.
- Add explicit CSV file-size limits.
- Add explicit maximum bulk row limits.
- Add more detailed bulk-job failure information.
- Add Celery retry policies for recoverable failures.
- Add stronger password requirements.
- Add account-management functionality.
- Add JWT refresh and revocation if required.
- Add production secret management.
- Add structured application metrics.
- Add monitoring and alerting.
- Add distributed tracing.
- Add CI pipelines for pytest.
- Add CI migration validation using `alembic check`.
- Add deployment-specific HTTPS configuration.
- Add reverse-proxy configuration for production.
- Add database backup and recovery procedures.
- Improve ticket-specific sentiment analysis.
- Improve summarization for short or domain-specific tickets.
- Expand model evaluation as more reviewed data becomes available.
- Add model drift monitoring.
- Formalize model versioning and deployment workflows.

---

# Final Project Status

The current implementation provides the complete primary application workflow using:

```text
FastAPI
PostgreSQL
Redis
Celery
Docker
SQLAlchemy
Alembic
JWT Authentication
Machine Learning
NLP Services
```

Implemented application capabilities include:

- user registration
- user login
- JWT authentication
- password hashing
- protected endpoints
- user data isolation
- single-ticket classification
- category prediction
- priority prediction
- suggested-team prediction
- summarization
- sentiment analysis
- prediction post-processing
- classification validation
- unclassified-ticket storage
- single manual review
- bulk manual review
- training-feedback collection
- CSV bulk processing
- Celery background tasks
- Redis task transport
- PostgreSQL persistence
- bulk-job status tracking
- classified bulk-result retrieval
- unclassified bulk-result retrieval
- per-user reporting
- authentication rate limiting
- structured application errors
- request logging
- request IDs
- Alembic migrations
- PostgreSQL health checks
- Redis health checks
- dependency-aware container startup
- non-root application containers
- automated smoke/security tests
- test coverage reporting
- Docker Compose deployment

The complete Docker workflow has been exercised successfully with:

```text
PostgreSQL Healthy
        +
Redis Healthy
        |
        v
FastAPI Running
        +
Celery Worker Ready
        |
        v
Authentication
        |
        v
Single Classification
        |
        v
Ticket Retrieval
        |
        v
Bulk CSV Submission
        |
        v
Background Processing
        |
        v
Bulk Results
        |
        v
Manual Review
```

The project is suitable as a functional internship/development implementation of an AI-powered ticket-classification backend.

Before production deployment, the deployment environment should additionally address:

- secure secrets
- HTTPS
- infrastructure security
- database backups
- resource limits
- monitoring
- alerting
- expanded automated testing
- operational model monitoring
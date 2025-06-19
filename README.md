# Event Management CRM Backend

This project implements a backend server for an event management platform, focusing on user CRM, event registrations, and email sending capabilities. It is built using FastAPI, AWS DynamoDB, and SendGrid, following a best-practice architectural pattern.

## Table of Contents

1.  [Architecture Overview](#architecture-overview)
2.  [Technical Stack](#technical-stack)
3.  [Features](#features)
4.  [Local Development Setup](#local-development-setup)
5.  [API Endpoints](#api-endpoints)
6.  [Database Design (DynamoDB)](#database-design-dynamodb)
7.  [Scalability and Maintainability](#scalability-and-maintainability)
8.  [Future Enhancements](#future-enhancements)
9.  [Testing](#testing)

## 1. Architecture Overview

The application follows a **Hexagonal Architecture (Ports and Adapters)** principle, implemented with a **Repository Pattern** and a clear separation of concerns into layers:

* **API Layer (`app/api`):** Handles HTTP requests, validates input using Pydantic schemas, and delegates to the Service layer. Uses FastAPI's `APIRouter` for modularity and `Depends` for dependency injection.
* **Service Layer (`app/services`):** Contains the core business logic. It orchestrates operations, uses repositories to interact with the database, and integrates with external services (like SendGrid).
* **Repository Layer (`app/repositories`):** Provides an abstraction over the data storage. Each repository handles CRUD operations for a specific entity against AWS DynamoDB. It encapsulates DynamoDB-specific logic.
* **Models Layer (`app/models`):** Defines the data structures using Pydantic, representing the entities (User, Event) stored in the database.
* **Database Layer (`app/database`):** Manages the connection to AWS DynamoDB.
* **Core Layer (`app/core`):** Holds application-wide configurations, custom exceptions, and utility functions.

This layered approach promotes:
* **Separation of Concerns:** Each layer has a distinct responsibility.
* **Testability:** Layers can be tested in isolation by mocking dependencies.
* **Maintainability:** Easier to understand, debug, and modify specific parts of the codebase.
* **Scalability:** The stateless nature of FastAPI and asynchronous operations support horizontal scaling.

## 2. Technical Stack

* **Backend Framework:** FastAPI (Python)
* **Database:** AWS DynamoDB (NoSQL)
* **Email Service:** SendGrid
* **Asynchronous Operations:** `asyncio`
* **Data Validation/Serialization:** Pydantic
* **AWS SDK:** `boto3`
* **Environment Management:** `python-dotenv`
* **API Server:** Uvicorn

## 3. Features

* **CRM System:**
    * User profile management (creation, retrieval, update, deletion).
    * Tracking of user event participation and hosting history (via relationships).
* **Query Functionality:**
    * Filter users by `company`, `job title`, `city`, `state`.
    * Support for combining multiple filter criteria.
    * Pagination and sorting options for user listings.
    * (Future: Filtering by number of events hosted/attended ranges - requires DynamoDB GSI design for efficient range queries or analytics layer.)
* **Email Sending:**
    * Endpoint to send emails to users based on filter criteria or explicit recipient lists.
    * Integration with SendGrid for reliable email delivery.
    * Basic tracking of email sending status (sent/failed counts).
* **Scalability & Maintainability:**
    * Modular architecture with clear separation of concerns.
    * Asynchronous I/O operations for high concurrency.
    * Dependency Injection for flexible and testable code.

## 4. Local Development Setup

### Prerequisites

* Python 3.9+
* Docker (Optional, for local DynamoDB)
* AWS Account with configured credentials (or local DynamoDB)
* SendGrid Account with an API Key and a verified sender email

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd event-crm-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project and populate it with your credentials:
    ```dotenv
    AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
    AWS_REGION_NAME=ap-southeast-1 # Or your desired AWS region
    SENDGRID_API_KEY=YOUR_SENDGRID_API_KEY
    SENDGRID_SENDER_EMAIL=your_verified_sender_email@example.com
    DYNAMODB_TABLE_PREFIX=EventCRM # Prefix for your DynamoDB tables
    ```
    **Important:** Do not commit `*.env` to your version control. It's already included in `.gitignore`.

5.  **Run Local DynamoDB (Optional, for local testing without AWS credentials):**
    If you want to run DynamoDB locally instead of connecting to AWS:
    ```bash
    docker run -p 8000:8000 amazon/dynamodb-local
    ```
    You would then modify `app/database/dynamodb_connector.py` to connect to `http://localhost:8000` and potentially remove the AWS credentials from the Boto3 client initialization for local testing only. For this assignment, the default setup connects to AWS.

6.  **Run the FastAPI Application:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The `--reload` flag enables live reloading during development. The `--host 0.0.0.0` makes the server accessible from any IP address on your network (useful if running in a VM/container).

7.  **Access the API Documentation:**
    Open your web browser and navigate to `http://127.0.0.1:8000/docs` to access the interactive OpenAPI (Swagger UI) documentation, where you can test the API endpoints.

## 5. API Endpoints

All API endpoints are prefixed with `/api/v1`.

### Users (`/api/v1/users`)

* `POST /`: Create a new user.
* `GET /{user_id}`: Retrieve a user by ID.
* `PUT /{user_id}`: Update an existing user.
* `DELETE /{user_id}`: Delete a user.
* `GET /`: Filter users by `company`, `job_title`, `city`, `state`, `min_events_hosted`, `max_events_hosted`, `min_events_attended`, `max_events_attended`, with pagination and sorting.

### Emails (`/api/v1/emails`)

* `POST /send-emails`: Send emails to users based on filter criteria or explicit recipient lists.

(Add details for Event endpoints if implemented)

## 6. Database Design (DynamoDB)

### User Table (`EventCRMUsers`)

* **Primary Key:** `id` (Partition Key, String)
* **Attributes:** `firstName`, `lastName`, `phoneNumber`, `email`, `avatar`, `gender`, `jobTitle`, `company`, `city`, `state`, `createdAt`, `updatedAt`.
* **Global Secondary Indexes (GSIs):**
    * `CompanyIndex`: Partition Key `company`
    * `JobTitleIndex`: Partition Key `jobTitle`
    * `CityStateIndex`: Partition Key `city`, Sort Key `state`
    These GSIs are designed to efficiently support filtering users by company, job title, and combined city/state.

### Event Table (`EventCRMEvents`) - *Conceptual, to be implemented*

* **Primary Key:** `id` (Partition Key, String)
* **Attributes:** `slug`, `title`, `description`, `startAt`, `endAt`, `venue`, `maxCapacity`, `ownerId`, `hosts`, `createdAt`, `updatedAt`.

### User-Event Relationships (`EventCRMUserEvents`) - *Conceptual, for event participation/hosting*

* This table would model the many-to-many relationship between users and events.
* **Primary Key:** `userId` (Partition Key), `eventId` (Sort Key) - for querying events by user.
* **GSI:** `eventId` (Partition Key), `userId` (Sort Key) - for querying participants/hosts by event.
* **Attributes:** `role` ("participant", "host"), `registeredAt`.

**Note on Analytics (Event Counts):** For efficient queries on `number of events hosted` or `number of events attended`, DynamoDB requires careful schema design. A common approach is to maintain these counts as attributes on the `User` item, updated atomically (e.g., using `UpdateItem` with `ADD` operation) when a user hosts or attends an event. This allows querying using `FilterExpression` on these attributes, though range queries on non-indexed attributes can still be less efficient for very large datasets. For complex analytical queries, consider an external analytics solution (e.g., streaming to S3/Athena or integrating with Elasticsearch).

## 7. Scalability and Maintainability

* **Asynchronous Processing:** All I/O operations (database, external APIs) are asynchronous, preventing blocking and allowing FastAPI to handle a large number of concurrent requests efficiently.
* **Modularity:** The project's layered architecture and use of FastAPI's `APIRouter` lead to a highly modular codebase. Each component (repository, service, endpoint) has a single responsibility, making it easier to understand, test, and maintain independently.
* **Dependency Injection:** Through FastAPI's `Depends`, dependencies are explicitly defined and injected, leading to loosely coupled components and greatly simplifying unit and integration testing.
* **Pydantic Models:** Enforce strict data validation for incoming requests and outgoing responses, reducing bugs and providing automatic API documentation.
* **Environment Variables:** Sensitive configurations and environment-specific settings are loaded from `.env` files, ensuring security and easy deployment to different environments.
* **Error Handling:** Uses FastAPI's `HTTPException` for consistent error responses.
* **Unit and Integration Tests:** (To be implemented) A comprehensive test suite would ensure the reliability and correctness of the application.

## 8. Future Enhancements

* **Comprehensive Testing:** Implement extensive unit, integration, and end-to-end tests.
* **Event Management:** Implement full CRUD for events and integrate with user event participation.
* **Authentication & Authorization:** Add JWT-based authentication for user access control and role-based authorization.
* **Background Tasks/Task Queue:** For high-volume email sending or other long-running operations, integrate a task queue (e.g., Celery with Redis/RabbitMQ, AWS SQS + Lambda) to offload tasks from the main API process.
* **Logging & Monitoring:** Implement structured logging (e.g., using `loguru`) and integrate with a monitoring solution (e.g., Prometheus, Grafana, AWS CloudWatch).
* **Dockerization:** Provide `Dockerfile` and `docker-compose.yml` for easy containerized deployment.
* **CI/CD Pipeline:** Automate the build, test, and deployment process.
* **Advanced Analytics:** Integrate with a dedicated analytics platform (e.g., AWS Kinesis/S3/Athena, Elasticsearch) for complex queries on event attendance and user engagement that might be inefficient with direct DynamoDB queries.
* **Email Templating:** Implement a proper email templating system (e.g., Jinja2) within the `EmailService` or leverage SendGrid's dynamic templates more fully.

## 9. Testing

(Details on how to run tests, what frameworks are used, etc.)
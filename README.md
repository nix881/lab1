# FastAPI Docker Application with MariaDB and Redis

This project is a Dockerized FastAPI application running on version 3.9. The application interacts with a MariaDB database and a Redis-based Valkey service. FastAPI is exposed on port 8000 and provides a Swagger UI documentation at `/docs`.

## Technologies Used:
- **FastAPI** - A modern, fast (high-performance), web framework for building APIs with Python 3.6+.
- **MariaDB** - A popular open-source relational database.
- **Valkey** - A Redis-based key-value store.
- **Docker** - For containerizing the application and its services.

## Requirements:
- Docker
- Docker Compose

## Project Structure:

- **FastAPI Application (app)**: Runs the FastAPI app on port 8000.
- **MariaDB**: A MariaDB database with pre-configured user credentials and database.
- **Valkey**: A Redis-based key-value service used in the app.

## Services:

- **app**: The FastAPI application that interacts with the database and Valkey.
- **mariadb**: MariaDB service.
- **valkey**: Redis-based Valkey service for storing key-value pairs.

## Docker Compose Configuration

The `docker-compose.yml` file defines three services:

## Build and Start the Services:

```bash
docker-compose up --build
```

## Access the Application:

Once the services are up and running, you can access the FastAPI application in your browser:
- **Application**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
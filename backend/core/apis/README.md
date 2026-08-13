# APIs

This folder contains the HTTP-facing part of the backend.

What this layer does:

- Creates the FastAPI app
- registers middleware
- includes routers
- defines request and response schemas
- accepts incoming HTTP requests

Files and folders here:

- `api.py`: creates the FastAPI app and registers routers/middleware
- `routes/`: endpoint functions such as login, register, or get profile
- `schemas/`: request and response models used by FastAPI validation

How it fits in the request flow:

1. Client sends HTTP request
2. Router receives it
3. Router validates input using schema classes
4. Router calls a controller
5. Controller returns data
6. FastAPI shapes the response using response schemas

Beginner note:

- Keep routers thin
- Do not write heavy business logic directly in route functions

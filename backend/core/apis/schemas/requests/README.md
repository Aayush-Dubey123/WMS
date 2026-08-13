# Request Schemas

This folder contains schemas for incoming request payloads.

These classes are used when a client sends data to the API.

Example:

- A register endpoint receives first name, last name, and email
- A login endpoint receives email and password

Why this folder exists:

- to validate user input before business logic runs
- to keep route functions clean
- to make request formats easy to understand

Current file:

- `user_request.py`: request schemas related to user registration, login, update, and password reset

Beginner note:

- If the client sends data into the server, the schema usually belongs here

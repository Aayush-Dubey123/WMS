# Response Schemas

This folder contains schemas for API responses.

These classes define what the backend sends back to the client.

Why response schemas are useful:

- they hide internal fields such as hashed passwords
- they keep response format consistent
- they make documentation cleaner in Swagger/OpenAPI

Current file:

- `user_responses.py`: response schemas for user profile data, login output, and generic messages

Beginner note:

- If the server is returning data to the client, the schema usually belongs here

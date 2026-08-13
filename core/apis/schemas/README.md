# Schemas

This folder contains Pydantic schema classes used by FastAPI.

Why schemas matter:

- they validate incoming request data
- they define the shape of outgoing response data
- they make API contracts clear and predictable

Subfolders:

- `requests/`: schemas for incoming request bodies
- `responses/`: schemas for API responses

Beginner note:

- Schemas are not database models
- Schemas describe API data
- Models describe stored database data

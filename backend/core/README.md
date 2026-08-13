# Core

This is the main application package.

The `core` folder contains the actual backend architecture:

- API layer
- controllers
- CRUD classes
- database setup
- models
- internal utilities

Think of `core` as the place where the app's business code lives.

Subfolders in this package:

- `apis`: HTTP layer, routes, and request/response schemas
- `controllers`: business logic
- `cruds`: database operations
- `database`: connection setup and database base classes
- `models`: MongoDB/ODMantic models
- `utils`: feature-specific helper code

Beginner note:

- When reading the code, start from `apis`, then go to `controllers`, then `cruds`, then `models`
- That is the usual request flow in this tutorial

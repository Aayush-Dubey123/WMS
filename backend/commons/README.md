# Commons

This folder contains shared helper code that can be used from anywhere in the project.

What belongs here:

- Reusable utility functions that are not tied to one feature
- Authentication helpers used across multiple routes or controllers
- Logging helpers used across the whole backend

Files in this folder:

- `auth.py`: JWT creation, JWT decoding, password hashing, and password verification
- `logger.py`: shared logger setup so every module logs in the same format

How it fits in the project:

- Routers, controllers, and CRUD classes can all import from `commons`
- This avoids repeating the same helper code in multiple places

Beginner note:

- If a file can be reused by many layers, it usually belongs in `commons`
- If a file belongs to one feature only, keep it inside `core`

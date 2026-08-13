# Models

This folder contains ODMantic model classes.

What models represent:

- the structure of data stored in MongoDB
- field types such as strings, emails, enums, and timestamps
- rules about what a stored document looks like

Current file:

- `user_model.py`: user document model with fields like name, email, password hash, role, and status

How models differ from schemas:

- models are for database storage
- schemas are for API input and output

Beginner note:

- If you want to define how data is stored in MongoDB, start in `models`

# CRUDs

This folder contains the data access layer.

CRUD stands for:

- Create
- Read
- Update
- Delete

What this layer does:

- talks to the database
- saves documents
- fetches documents
- updates documents
- deletes documents

Files in this folder:

- `base.py`: generic reusable CRUD operations shared by many models
- `user_crud.py`: user-specific queries such as finding a user by email

Beginner note:

- Controllers decide what should happen
- CRUD classes perform the database work needed to make that happen

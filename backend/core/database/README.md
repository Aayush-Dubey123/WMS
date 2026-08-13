# Database

This folder contains the database setup for the tutorial.

What this folder teaches:

- how to connect to MongoDB
- how to keep one shared connection using a singleton
- how ODMantic sits on top of Motor
- how models inherit from a common base class

Files in this folder:

- `database.py`: MongoDB client creation, ODMantic engine creation, ping, connect, and close logic
- `base_class.py`: shared base model used by ODMantic models

Beginner note:

- This folder handles connection setup
- Actual feature queries are written in the `cruds` folder

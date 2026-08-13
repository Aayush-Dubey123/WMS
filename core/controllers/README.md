# Controllers

This folder contains the business logic layer.

What controllers do:

- apply rules to incoming data
- call one or more CRUD methods
- call helpers such as email sending or JWT creation
- decide what should happen for a feature

Example from this tutorial:

- `user_controller.py` checks whether a user already exists, hashes passwords, creates tokens, and sends welcome emails

What controllers should not do:

- define routes
- handle raw HTTP details when avoidable
- contain low-level database query code

Beginner note:

- If a route says "what endpoint was called", the controller says "what business action should happen"

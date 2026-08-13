# Routes

This folder contains the route modules.

Each route file usually groups endpoints by feature.

In this tutorial:

- `auth_router.py` handles registration and login endpoints
- `user_router.py` handles authenticated user profile endpoints

What a router should do:

- define the URL path
- define the HTTP method such as GET or POST
- accept validated request data
- call the controller layer
- return the final response

What a router should not do:

- complex business logic
- direct database query code
- large reusable helper logic

Beginner note:

- A router is the entry point for one request
- Keep it easy to read so learners can follow the flow quickly

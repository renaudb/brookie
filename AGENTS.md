# AGENTS.md

# Backend
- Use strict type checking.
- Structure the code using models, commands and API endpoints.
    - Models define SQL alchemy models.
    - Commands define operations on models.
    - API endpoints define the API routing logic. 
- Use a flat API structure without nested routes.
- Use uuid7 for all ids.
- Do not make changes to migration files unless explicitly asked to.

# Frontend
- Use strict type checking.
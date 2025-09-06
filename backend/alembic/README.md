# Alembic Migration Guide

This README provides instructions for running database migrations using Alembic in this project.

## Common Alembic Commands

### 1. Create a New Migration
Autogenerate a migration after changing SQLAlchemy models:
```
alembic revision --autogenerate -m "Describe your change"
```

### 2. Apply Migrations to the Database
Apply all pending migrations:
```
alembic upgrade head
```

### 3. View Migration History
Show the list of applied and pending migrations:
```
alembic history
```

### 4. Downgrade the Database
Revert the last migration:
```
alembic downgrade -1
```
Or revert to a specific revision:
```
alembic downgrade <revision_id>
```

### 5. Check Current Migration Version
Show the current migration version in the database:
```
alembic current
```

## Configuration
- The database URL is set in `alembic.ini`.
- Alembic uses models from `database/models.py`.
- Migration scripts are stored in `alembic/versions/`.

## Tips
- Always commit your migration scripts to version control.
- If you change your models, always generate and apply a new migration.

For more details, see the [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/).


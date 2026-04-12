# Cleanup

Remove everything created by this project:

```bash
docker compose down --remove-orphans
```

## What this removes

- containers from this Compose project
- the network created for this Compose project
- the PostgreSQL data stored in the container
- the Airflow metadata stored in the PostgreSQL container

## Result

This removes the local pipeline environment and the generated database contents.

The next `docker compose up -d` run starts the services again from a clean state.

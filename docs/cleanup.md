# Cleanup

Remove everything created by this project:

```bash
docker compose down --volumes --rmi local --remove-orphans
```

## What this removes

- containers from this Compose project
- networks created for this Compose project
- named volumes from this Compose project, including `pgdata`
- the local image built for the `app` service
- orphaned containers belonging to this Compose project

## Result

Because the PostgreSQL volume is removed, this also deletes all generated database tables, including:

- raw tables
- analytics tables
- summary tables

The next `docker compose up --build` run starts from a clean state.

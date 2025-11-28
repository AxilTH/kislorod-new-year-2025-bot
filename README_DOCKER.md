Quick Docker Postgres setup for this project

1) Copy `.env.example` to `.env` and fill values (at minimum set `POSTGRES_PASSWORD`).

2) On your Ubuntu VPS run the helper script (as root or with sudo):

```bash
sudo bash scripts/setup_docker_db.sh
```

This installs Docker and docker-compose plugin, then starts the `postgres` service defined in `docker-compose.yml`.

3) Verify the DB is running:

```bash
docker ps
# or
/usr/bin/docker compose ps
```

4) Set `TARGET_DB_URL` in your `.env` if you want a custom connection string, otherwise `config.py` will build it from `POSTGRES_*` variables.

Example `TARGET_DB_URL` value:

```
postgresql+asyncpg://postgres:yourpassword@127.0.0.1:5432/kislorod
```

5) Start your app (from project root):

```bash
python run.py
# or
uvicorn app.api.main:app --reload --port 8000
```

Notes
- The script installs packages from Docker's official repository.
- The script maps Postgres port to the host. If you run multiple DBs or need to restrict access, adjust `docker-compose.yml`.
- For production consider using managed Postgres or more secure configuration (non-default passwords, backups, network restrictions).
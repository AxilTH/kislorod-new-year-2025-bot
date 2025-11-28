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

Run everything with Docker Compose
--------------------------------

The `docker-compose.yml` now defines three services: `postgres`, `api` and `bot`.
Use Docker Compose to build the image and start all services together:

```bash
# build images and start services in background
docker compose up -d --build

# check services
docker compose ps
```

Accessing the API and database from your workstation
---------------------------------------------------

- API (Postman): the `api` service is bound to host port `8000`. If your VPS IP is `45.11.92.14`, call:

	`http://45.11.92.14:8000/docs`

	or any API endpoint, e.g. `http://45.11.92.14:8000/tasks`.

- Database (BeekeeperStudio / DB client): the `postgres` service maps container port 5432 to the host port (default `5432`). Connect to:

	Host: `45.11.92.14`
	Port: `5432`
	User: value of `POSTGRES_USER` in `.env` (default `postgres`)
	Password: value of `POSTGRES_PASSWORD` in `.env`
	Database: value of `POSTGRES_DB` in `.env`

Important notes about `.env` and `TARGET_DB_URL`
------------------------------------------------

- If you have a `TARGET_DB_URL` set in your local `.env` that points to `localhost` (for example `postgresql+asyncpg://postgres:pass@localhost:5432/...`), the containers will inherit it unless overridden. Inside the containers `localhost` means the container itself, so the app would not reach the `postgres` service. To avoid this:
	- Either remove `TARGET_DB_URL` from `.env` and rely on `POSTGRES_*` variables, or
	- Set `TARGET_DB_URL` to point to the `postgres` service (compose already sets `TARGET_DB_URL` for `api` and `bot` to use `postgres://...@postgres:5432/...`).

Quick troubleshooting
---------------------
- If the API is not reachable externally, ensure the app is listening on `0.0.0.0` (compose runs it like that) and that your server firewall/cloud security group allows inbound TCP on port `8000` and `5432`.
- To avoid exposing ports in production, use an SSH tunnel for Postman or a reverse proxy with TLS (nginx + certbot).

Notes
- The script installs packages from Docker's official repository.
- The script maps Postgres port to the host. If you run multiple DBs or need to restrict access, adjust `docker-compose.yml`.
- For production consider using managed Postgres or more secure configuration (non-default passwords, backups, network restrictions).
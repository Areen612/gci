# Database Provisioning Guide

This guide explains how to provision PostgreSQL databases for the GCI project across development, staging, and production environments. It covers allocating an instance, configuring database users, and handling credentials securely.

## 1. Allocate a PostgreSQL instance

You can provision PostgreSQL in two different ways:

### Managed cloud database
1. Request a managed PostgreSQL 15 instance from your cloud provider (AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL, etc.).
2. Size the instance according to the target environment:
   - **Development:** smallest instance class with minimal storage.
   - **Staging:** mirror production class if possible to ensure parity.
   - **Production:** follow your reliability/SLA requirements (multi-AZ, automated backups, point-in-time recovery).
3. Record the hostname, port, and administrative credentials in your secret manager (see [Secrets](#3-document-connection-details-and-store-secrets)).

### Local Docker Compose instance
For local development, you may provision Postgres using the provided Compose file:

```bash
cp .env.example .env
# Edit .env with secure passwords before continuing.
docker compose -f docker-compose.postgres.yml --profile dev up -d
```

The Compose service exposes Postgres on port `5432`. Staging and production profiles are available for parity testing if you need local replicas:

```bash
# Staging simulation
docker compose -f docker-compose.postgres.yml --profile staging up -d

# Production simulation
docker compose -f docker-compose.postgres.yml --profile prod up -d
```

## 2. Create databases, users, and permissions per environment

When the container starts, the script at `docker/postgres/initdb/10_create_envs.sh` creates one database and one login role per environment (`gci_dev`, `gci_staging`, `gci_prod`). Each role is granted ownership of its database so that migrations can run without superuser privileges.

For managed cloud instances, execute the same script manually from an administrative session:

```bash
# Load environment variables securely before running this script.
export PGHOST=your-managed-hostname
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=...
export DEV_DB_PASSWORD=...
export STAGING_DB_PASSWORD=...
export PROD_DB_PASSWORD=...

./docker/postgres/initdb/10_create_envs.sh
```

The script performs the following for each environment:

- Creates a login role (`gci_<env>`) using the password from the corresponding environment variable.
- Creates a database (`gci_<env>`) owned by that role.
- Grants ownership so that the application can manage schema objects.

If you prefer to manage permissions manually, the SQL equivalent for development is:

```sql
CREATE ROLE gci_dev LOGIN PASSWORD '…';
CREATE DATABASE gci_dev OWNER gci_dev;
GRANT ALL PRIVILEGES ON DATABASE gci_dev TO gci_dev;
```

Repeat for staging and production, substituting the role, database, and password.

## 3. Document connection details and store secrets

Store database credentials in your secret manager of choice (HashiCorp Vault, AWS Secrets Manager, 1Password, etc.). For local work, populate the `.env` file created above. Do **not** commit the `.env` file to version control.

| Environment | Connection URL template |
|-------------|-------------------------|
| Development | `postgres://gci_dev:<DEV_DB_PASSWORD>@<host>:5432/gci_dev` |
| Staging     | `postgres://gci_staging:<STAGING_DB_PASSWORD>@<host>:5432/gci_staging` |
| Production  | `postgres://gci_prod:<PROD_DB_PASSWORD>@<host>:5432/gci_prod` |

Update the following secrets for each environment:

- `POSTGRES_SUPERUSER_PASSWORD`
- `DEV_DB_PASSWORD`
- `STAGING_DB_PASSWORD`
- `PROD_DB_PASSWORD`
- (Optional) full `*_DATABASE_URL` strings for application deployment pipelines.

For teams using Vault, store the values under paths such as:

```
vault kv put secret/gci/dev/database url=$DEV_DATABASE_URL password=$DEV_DB_PASSWORD
vault kv put secret/gci/staging/database url=$STAGING_DATABASE_URL password=$STAGING_DB_PASSWORD
vault kv put secret/gci/prod/database url=$PROD_DATABASE_URL password=$PROD_DB_PASSWORD
```

When deploying, applications should read the appropriate secret and set the `DATABASE_URL` environment variable.

## 4. Verifying access

After provisioning, confirm connectivity for each environment:

```bash
psql "${DEV_DATABASE_URL}"
psql "${STAGING_DATABASE_URL}"
psql "${PROD_DATABASE_URL}"
```

Run a simple query to ensure the user has the expected permissions:

```sql
SELECT current_user, current_database();
```

## 5. Maintenance considerations

- Rotate passwords periodically and update the stored secrets.
- Enable automated backups (cloud) or volume snapshots (Docker) as required.
- Ensure staging mirrors production settings to catch performance issues early.

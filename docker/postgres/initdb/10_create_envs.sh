#!/usr/bin/env bash
set -euo pipefail

: "${DEV_DB_PASSWORD:?DEV_DB_PASSWORD must be set}"
: "${STAGING_DB_PASSWORD:?STAGING_DB_PASSWORD must be set}"
: "${PROD_DB_PASSWORD:?PROD_DB_PASSWORD must be set}"

PSQL_USER=${POSTGRES_USER:-${PGUSER:-postgres}}

psql -v ON_ERROR_STOP=1 --username "$PSQL_USER" <<-SQL
    DO
    $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'gci_dev') THEN
            CREATE ROLE gci_dev LOGIN PASSWORD '${DEV_DB_PASSWORD}';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gci_dev') THEN
            CREATE DATABASE gci_dev OWNER gci_dev;
        END IF;
    END
    $$;

    DO
    $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'gci_staging') THEN
            CREATE ROLE gci_staging LOGIN PASSWORD '${STAGING_DB_PASSWORD}';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gci_staging') THEN
            CREATE DATABASE gci_staging OWNER gci_staging;
        END IF;
    END
    $$;

    DO
    $$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'gci_prod') THEN
            CREATE ROLE gci_prod LOGIN PASSWORD '${PROD_DB_PASSWORD}';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'gci_prod') THEN
            CREATE DATABASE gci_prod OWNER gci_prod;
        END IF;
    END
    $$;
SQL

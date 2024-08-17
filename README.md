# 15GG Backend

> Backend repository of 15GG implemented in FastAPI

## Services
```
PostgreSQL v14.5
Python v3.10
Nginx v1.22.0
```

## Getting Started

### 1. Prerequistes
```
Docker v20.10+
Docker Compose v2.10.2+
```
### 2. Set environment variables

create a `.env` file at the root directory

```
DB_HOST={Hostname of DBMS. Defaults to 127.0.0.1}
DB_PORT={Post of DBMS. Defaults to 5432}
DB_USERNAME={Login username for DBMS}
DB_PASSWORD={Login password for DBMS}
DB_NAME={Name of database.}
RIOT_TOKEN={Access token for Riot API}

ex)
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_USERNAME="admin_15gg"
DB_PASSWORD="admin_15gg"
DB_NAME="db_15gg"
RIOT_TOKEN="RGAPI-cb0b2e45-b6bc-4a81-b67f-2cec7269a28b"
```


The project directory should be like
```
.
├── app
│   ├── __init__.py
│   ├── api
│   ├── core
│   ├── crud
│   ├── database
│   ├── models
│   ├── schemas
│   └── main.py
└── migrations
│   ├── versions
│   ├── env.py
│   └── script.py.mako
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── Pipfile
├── Pipfile.lock
├── README.md
└── requirements.txt
```

### 3. Launch containers

```
> docker compose up -d
```

### 3-1. For Development Environment
```
> docker compose up -d db
> uvicorn app.main:app --reload
```
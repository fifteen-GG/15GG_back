# 15GG Backend

> Backend repository of 15GG implemented in FastAPI

## Getting Started

### Prerequistes
```
Python 3.10+
PostgreSQL 14.5+
```
### Set environment variables

create `.env` file at root directory

```
DB_HOST={Hostname of DBMS. Defaults to 127.0.0.1}
DB_PORT={Post of DBMS. Defaults to 5432}
DB_USERNAME={Login username for DBMS}
DB_PASSWORD={Login password for DBMS}
DB_NAME={Name of database.}

ex)
DB_HOST="127.0.0.1"
DB_PORT="5432"
DB_USERNAME="admin_15gg"
DB_PASSWORD="admin_15gg"
DB_NAME="db_15gg"
```


The project directory should be like
```
app/
├─ api/
├─ core/
├─ crud/
├─ database/
├─ models/
├─ schemas/
├─ main.py
migrations/
.env
.gitignore
alembic.ini
Pipfile
Pipfile.lock
README.md
```

### Launch virtual environment

```
> pipenv install
> pipenv shell
```

### Migrate Database

```
> python3 -m alembic upgrade head
```

### Start app

```
> python3 -m app.main
```
---
name: project-architecture
description: Use when adding new files, restructuring, or deciding where to put new functionality in movie-kg-api. Covers module layout, separation of concerns, naming, and when to refactor.
---

# movie-kg-api Architecture

## Layout

```
movie-kg-api/
├── app/                     # ← all Python code lives here
│   ├── __init__.py
│   ├── main.py              # FastAPI app + middleware + router registration
│   ├── config/
│   │   ├── __init__.py      # re-exports: driver, logger
│   │   ├── db.py            # Neo4j driver singleton
│   │   └── logger.py        # Rich colored logger
│   ├── models/
│   │   ├── __init__.py      # re-exports: Movie, Person
│   │   ├── movie.py         # one file per Pydantic model
│   │   └── person.py
│   └── routers/
│       ├── __init__.py
│       ├── movies.py
│       ├── people.py
│       ├── relationships.py
│       └── seed.py
├── Dockerfile               # container build (WORKDIR=/code)
├── compose.yaml             # api + neo4j services
├── requirements.txt
├── .env                     # secrets (gitignored)
├── .dockerignore
└── .gitignore
```

Infra/config at root, code inside `app/`. Clean separation.

## Import style

Relative imports inside `app/` package:

```python
# app/main.py
from .config import driver, logger
from .routers import movies

# app/routers/movies.py
from ..config import driver, logger
from ..models import Movie
```

## Where does new code go?

| Adding | File |
|---|---|
| New endpoint for movies | `app/routers/movies.py` |
| New endpoint for people | `app/routers/people.py` |
| New relationship type | `app/routers/relationships.py` |
| New domain (e.g. Genre) | new file `app/routers/genres.py` + register in `main.py` |
| New Pydantic model | new file `app/models/<name>.py` + re-export in `models/__init__.py` |
| DB connection / helper | `app/config/db.py` |
| Logger tweak | `app/config/logger.py` |
| Middleware / app-wide config | `main.py` |

## Separation of concerns

- `app/routers/*` → HTTP concerns (paths, status codes, validation)
- Cypher → inline in routers for now; extract to `services/` or `queries.py` once reused
- `db.py` → connection management only
- `models.py` → data shapes, no behavior
- `logger.py` → logging config only

## When to refactor

| Trigger | Refactor |
|---|---|
| Same Cypher in 2+ places | Extract to a service/repository |
| Router > ~150 lines | Split by subdomain |
| Many Pydantic models | Move to `schemas/` folder |
| Business logic across domains | Add `services/` layer |

## Naming conventions

- Routers: plural domain — `movies.py`, `people.py`, `genres.py`
- Models: singular — `Movie`, `Person`, `Genre`
- Endpoints: REST — `GET /movies`, `POST /movies`, `GET /movies/{title}`
- Relationship endpoints: nested — `POST /movies/{title}/actors/{name}`

## Import rules

- Routers import from `db`, `models`, `logger`
- Routers never import other routers
- `main.py` imports routers to register them
- Keep shared types in `models.py` → avoids circular imports

## Adding a new domain — checklist

1. Create `models.py` class
2. Create `app/routers/<domain>.py` with `router = APIRouter(prefix=..., tags=...)`
3. Add endpoints
4. Register in `main.py`: `app.include_router(<domain>.router)`
5. Update seed if needed
6. Add index for lookup property

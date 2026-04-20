---
name: fastapi-patterns
description: Use when adding/modifying FastAPI endpoints, routers, or Pydantic models in movie-kg-api. Covers dependency injection, response models, status codes, error handling, APIRouter organization.
---

# FastAPI Patterns for movie-kg-api

## Router organization

All endpoints live in `routers/*.py`. Never add endpoints directly to `main.py`.

Each router = one domain:
- `movies.py` → Movie nodes
- `people.py` → Person nodes
- `relationships.py` → edges (ACTED_IN, DIRECTED)
- `seed.py` → seed/maintenance

New domain? New file. Register in `main.py` with `app.include_router(...)`.

## APIRouter pattern

```python
from fastapi import APIRouter

router = APIRouter(prefix="/resource", tags=["resource"])

@router.get("")
def list_resource():
    ...
```

- `prefix` avoids repeating path segments
- `tags` groups endpoints in `/docs`

## Dependency injection for DB sessions

Replace repetitive `with driver.session()` with `Depends`:

```python
from fastapi import Depends

def get_session():
    with driver.session() as session:
        yield session

@router.get("")
def list_movies(session = Depends(get_session)):
    result = session.run(...)
```

Benefits: testable (override in tests), consistent lifecycle, less boilerplate.

## Response models

Declare output shapes explicitly:

```python
class MovieOut(BaseModel):
    title: str
    year: int
    genre: str

@router.get("", response_model=list[MovieOut])
def list_movies():
    ...
```

Auto-schema in `/docs`, validates output, strips extras.

## Status codes

Use `status` module, not raw ints:

```python
from fastapi import status

@router.post("", status_code=status.HTTP_201_CREATED)
def create_movie(...):
    ...

raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="...")
```

## Exception handlers

Centralize error shape in `main.py`:

```python
from neo4j.exceptions import Neo4jError

@app.exception_handler(Neo4jError)
async def neo4j_handler(request, exc):
    logger.error(f"[error]Neo4j error:[/] {exc}")
    return JSONResponse(status_code=503, content={"detail": "Database unavailable"})
```

## Validation with Field

Never trust input blindly:

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    year: int = Field(ge=1888, le=2100)
    genre: str
```

## Lifespan context (modern replacement for on_event)

`@app.on_event("startup"/"shutdown")` is deprecated. Use:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[success]✓ Starting[/]")
    yield
    logger.warning("[warning]⚠ Shutting down[/]")
    driver.close()

app = FastAPI(lifespan=lifespan)
```

## What NOT to do

- Don't put Cypher queries in `main.py`
- Don't bypass Pydantic — no `dict` as request body
- Don't return raw Neo4j `Node` — always `dict(node)`
- Don't catch bare `Exception:` — catch specific
- Don't f-string user input into Cypher

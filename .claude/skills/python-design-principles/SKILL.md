---
name: python-design-principles
description: Use when refactoring or adding non-trivial logic to movie-kg-api. Covers SOLID, composition over inheritance, repository/service patterns, when to reach for OOP vs functions, error philosophy.
---

# Design Principles for movie-kg-api

## Functions vs classes

**Functions (current default, keep using):**
- Pure transformations
- Simple request handlers
- Small utilities

**Classes:**
- Stateful services (DB driver, cache, repositories)
- Grouped operations with shared context
- Protocol/interface contracts

Current handlers are functions. Don't OOP-ify without reason.

## SOLID applied

### S — Single Responsibility
One function = one action. Bad: `create_and_link_and_log_and_email(...)`.

### O — Open/Closed
Extend via new files. Adding genres = new `routers/genres.py`, not editing `movies.py`.

### L — Liskov
If subclassing repositories, honor the base contract — don't weaken postconditions.

### I — Interface Segregation
Don't pass giant `ctx` objects. Inject only what's needed via `Depends(...)`.

### D — Dependency Inversion
Handlers depend on a `session` abstraction (via `Depends`), not on direct `driver.session()` calls. Makes testing trivial.

## Repository pattern (adopt when queries repeat)

```python
# repositories/movie.py
class MovieRepository:
    def __init__(self, session):
        self.session = session

    def find_by_title(self, title: str) -> dict | None:
        result = self.session.run(
            "MATCH (m:Movie {title: $title}) RETURN m", title=title
        )
        record = result.single()
        return dict(record["m"]) if record else None

    def create(self, movie: Movie) -> dict:
        ...
```

Handler becomes thin:

```python
@router.post("")
def create_movie(movie: Movie, repo: MovieRepository = Depends(get_movie_repo)):
    return repo.create(movie)
```

## Service layer (for cross-domain logic)

```python
class RecommendationService:
    def __init__(self, movie_repo, person_repo):
        self.movies = movie_repo
        self.people = person_repo

    def recommend_via_shared_actors(self, title: str) -> list[dict]:
        ...
```

Router → service → repositories. Clear layering.

## Composition over inheritance

```python
# BAD
class TimestampedMovie(Movie, Timestamped, Loggable): ...

# GOOD
class Movie(BaseModel):
    created_at: datetime
    # log via logger — don't mix in behavior
```

Pydantic models = data. Don't inherit behavior.

## Error handling philosophy

- Domain errors → custom exceptions (`MovieNotFound`, `InvalidRelationship`)
- HTTP errors → `HTTPException` at the router edge only
- Never swallow exceptions silently — log or re-raise
- Let unexpected errors bubble to the middleware → structured 500

Example:

```python
class MovieNotFound(Exception): ...

# In repository
def find_by_title(self, title):
    record = ...
    if not record:
        raise MovieNotFound(title)

# In router
try:
    return repo.find_by_title(title)
except MovieNotFound:
    raise HTTPException(404, f"Movie '{title}' not found")
```

## Avoid premature abstraction

- 3 duplicated lines → fine
- 5th duplication → extract
- Don't create `BaseRepository` until 3 repos exist
- Don't add config layers for hypothetical futures

## Immutability where possible

```python
class Movie(BaseModel):
    model_config = {"frozen": True}
    title: str
    year: int
```

DTOs flowing through the stack should be immutable.

## Naming

- Booleans: `is_`, `has_`, `can_` prefixes
- Functions: verb phrases (`find_movie`, `create_person`)
- Classes: noun phrases (`MovieRepository`, `RecommendationService`)
- Private: leading underscore (`_internal_helper`)

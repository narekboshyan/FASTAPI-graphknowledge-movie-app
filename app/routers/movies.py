from fastapi import APIRouter

from ..config import driver, logger
from ..models import Movie

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("")
def create_movie(movie: Movie):
    query = """
    MERGE (m:Movie {title: $title})
    ON CREATE SET m.year = $year, m.genre = $genre
    RETURN m
    """
    with driver.session() as session:
        result = session.run(
            query,
            title=movie.title,
            year=movie.year,
            genre=movie.genre,
        )
        record = result.single()
        logger.info(f"[success]✓ Movie created:[/] {movie.title}")
        return {"movie": dict(record["m"])}


@router.get("")
def list_movies(genre: str | None = None, limit: int = 10):
    query = """
    MATCH (m:Movie)
    WHERE $genre IS NULL OR m.genre = $genre
    RETURN m
    ORDER BY m.year DESC
    LIMIT $limit
    """
    with driver.session() as session:
        result = session.run(query, genre=genre, limit=limit)
        movies = [dict(record["m"]) for record in result]
        logger.info(f"[success]✓ Listed {len(movies)} movies[/]")
        return movies

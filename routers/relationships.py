from fastapi import APIRouter, HTTPException

from db import driver
from logger import logger

router = APIRouter(tags=["relationships"])


@router.post("/movies/{movie_title}/actors/{person_name}")
def add_actor_to_movie(movie_title: str, person_name: str):
    query = """
    MATCH (p:Person {name: $person_name})
    MATCH (m:Movie {title: $movie_title})
    MERGE (p)-[:ACTED_IN]->(m)
    RETURN p, m
    """
    with driver.session() as session:
        result = session.run(query, person_name=person_name, movie_title=movie_title)
        record = result.single()
        if not record:
            logger.warning(f"[warning]⚠ Not found:[/] {person_name} or {movie_title}")
            raise HTTPException(status_code=404, detail="Movie or person not found")
        logger.info(f"[success]✓ ACTED_IN:[/] {person_name} → {movie_title}")
        return {"message": f"{person_name} ACTED_IN {movie_title}"}


@router.post("/movies/{movie_title}/director/{person_name}")
def set_director(movie_title: str, person_name: str):
    query = """
    MATCH (p:Person {name: $person_name})
    MATCH (m:Movie {title: $movie_title})
    MERGE (p)-[:DIRECTED]->(m)
    RETURN p, m
    """
    with driver.session() as session:
        result = session.run(query, person_name=person_name, movie_title=movie_title)
        record = result.single()
        if not record:
            logger.warning(f"[warning]⚠ Not found:[/] {person_name} or {movie_title}")
            raise HTTPException(status_code=404, detail="Movie or person not found")
        logger.info(f"[success]✓ DIRECTED:[/] {person_name} → {movie_title}")
        return {"message": f"{person_name} DIRECTED {movie_title}"}

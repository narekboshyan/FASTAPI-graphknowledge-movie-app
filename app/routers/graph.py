from fastapi import APIRouter

from ..config import driver, logger

router = APIRouter(tags=["graph"])


@router.get("/people/{name}/filmography")
def get_filmography(name: str):
    query = """
    MATCH (p:Person {name: $name})-[:ACTED_IN]->(m:Movie)
    RETURN m.title AS title, m.year AS year, m.genre AS genre
    ORDER BY m.year DESC
    """
    with driver.session() as session:
        result = session.run(query, name=name)
        films = [dict(record) for record in result]
        logger.info(f"[success]✓ Filmography:[/] {name} — {len(films)} films")
        return films

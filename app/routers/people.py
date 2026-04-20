from fastapi import APIRouter

from ..config import driver, logger
from ..models import Person

router = APIRouter(prefix="/people", tags=["people"])


@router.post("")
def create_person(person: Person):
    query = """
    MERGE (p:Person {name: $name})
    ON CREATE SET p.born = $born
    RETURN p
    """
    with driver.session() as session:
        result = session.run(query, name=person.name, born=person.born)
        record = result.single()
        logger.info(f"[success]✓ Person created:[/] {person.name}")
        return {"person": dict(record["p"])}

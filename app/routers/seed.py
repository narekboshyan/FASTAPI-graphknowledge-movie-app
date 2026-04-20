from fastapi import APIRouter

from ..config import driver, logger

router = APIRouter(tags=["seed"])


@router.post("/seed")
def seed_data():
    wipe = "MATCH (n) DETACH DELETE n"
    create = """
    CREATE (inception:Movie {title: 'Inception', year: 2010, genre: 'sci-fi'})
    CREATE (interstellar:Movie {title: 'Interstellar', year: 2014, genre: 'sci-fi'})
    CREATE (matrix:Movie {title: 'The Matrix', year: 1999, genre: 'sci-fi'})
    CREATE (wolf:Movie {title: 'The Wolf of Wall Street', year: 2013, genre: 'drama'})
    CREATE (titanic:Movie {title: 'Titanic', year: 1997, genre: 'drama'})
    CREATE (johnwick:Movie {title: 'John Wick', year: 2014, genre: 'action'})

    CREATE (leo:Person {name: 'Leonardo DiCaprio', born: 1974})
    CREATE (keanu:Person {name: 'Keanu Reeves', born: 1964})
    CREATE (joseph:Person {name: 'Joseph Gordon-Levitt', born: 1981})
    CREATE (matthew:Person {name: 'Matthew McConaughey', born: 1969})
    CREATE (nolan:Person {name: 'Christopher Nolan', born: 1970})
    CREATE (wachowski:Person {name: 'Lana Wachowski', born: 1965})
    CREATE (stahelski:Person {name: 'Chad Stahelski', born: 1968})
    CREATE (scorsese:Person {name: 'Martin Scorsese', born: 1942})
    CREATE (cameron:Person {name: 'James Cameron', born: 1954})

    CREATE (leo)-[:ACTED_IN]->(inception)
    CREATE (leo)-[:ACTED_IN]->(wolf)
    CREATE (leo)-[:ACTED_IN]->(titanic)
    CREATE (joseph)-[:ACTED_IN]->(inception)
    CREATE (matthew)-[:ACTED_IN]->(interstellar)
    CREATE (matthew)-[:ACTED_IN]->(wolf)
    CREATE (keanu)-[:ACTED_IN]->(matrix)
    CREATE (keanu)-[:ACTED_IN]->(johnwick)

    CREATE (nolan)-[:DIRECTED]->(inception)
    CREATE (nolan)-[:DIRECTED]->(interstellar)
    CREATE (wachowski)-[:DIRECTED]->(matrix)
    CREATE (stahelski)-[:DIRECTED]->(johnwick)
    CREATE (scorsese)-[:DIRECTED]->(wolf)
    CREATE (cameron)-[:DIRECTED]->(titanic)
    """
    with driver.session() as session:
        session.run(wipe)
        session.run(create)
    logger.info("[success]✓ Graph seeded:[/] 6 movies, 9 people, 14 relationships")
    return {"message": "Graph seeded"}

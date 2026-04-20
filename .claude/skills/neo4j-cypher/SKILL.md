---
name: neo4j-cypher
description: Use when writing/modifying Cypher queries in movie-kg-api. Covers MERGE vs CREATE, parameterized queries, session lifecycle, transactions, indexes, result handling, traversal patterns.
---

# Neo4j Cypher Patterns

## MERGE vs CREATE

| Use case | Clause |
|---|---|
| Seed after wipe | `CREATE` (faster, no conflict possible) |
| Write endpoint (POST) | `MERGE` (idempotent — safe to retry) |
| Adding a relationship | `MERGE` (prevents duplicate edges) |

```cypher
MERGE (m:Movie {title: $title})
ON CREATE SET m.year = $year, m.genre = $genre
ON MATCH SET m.updated_at = timestamp()
```

## Parameterized queries (always)

```python
# GOOD
session.run("MATCH (m:Movie {title: $title}) RETURN m", title=value)

# BAD — injection risk, kills query plan cache
session.run(f"MATCH (m:Movie {{title: '{value}'}}) RETURN m")
```

## Result handling

```python
# Single expected
record = result.single()   # None if empty
if not record:
    raise HTTPException(404, "Not found")
node = dict(record["m"])

# Multiple
items = [dict(r["m"]) for r in result]
```

## Session lifecycle

Consume results **inside** the `with` block:

```python
with driver.session() as session:
    result = session.run(...)
    data = [r for r in result]  # consume here
# session closed → result is dead
```

## Transactions for multi-statement writes

Atomic. Rolls back on any error:

```python
def _link(tx, name, title):
    tx.run("MERGE (p:Person {name: $name})", name=name)
    tx.run(
        "MATCH (p:Person {name: $name}), (m:Movie {title: $title}) "
        "MERGE (p)-[:ACTED_IN]->(m)",
        name=name, title=title,
    )

with driver.session() as session:
    session.execute_write(_link, name="X", title="Y")
```

## Indexes (performance)

For every property used in MATCH lookups:

```cypher
CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title)
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)
```

Run at startup or in seed. Huge speedup at scale.

## Traversal patterns

| Pattern | Meaning |
|---|---|
| `(a)-[:R]->(b)` | One directed hop |
| `(a)-[:R*1..3]->(b)` | Variable length, 1-3 hops |
| `(a)-[:R]->(m)<-[:R]-(b)` | Common neighbor (co-actors) |
| `(a)-[:ACTED_IN]->(m)<-[:DIRECTED]-(d)` | Multi-type traversal |

## Aggregation

```cypher
MATCH (p:Person {name: $name})-[:ACTED_IN]->(m:Movie)
RETURN DISTINCT m.genre AS genre,
       count(m) AS count,
       collect(m.title) AS titles
ORDER BY count DESC
```

## Cleanup

```cypher
MATCH (n) DETACH DELETE n   # deletes node + all rels
```

Plain `DELETE` fails if node has relationships.

## What NOT to do

- Don't f-string user input into Cypher
- Don't return `result` outside `session` context
- Don't `MATCH (n) DELETE n` → use `DETACH DELETE`
- Don't MERGE on partial keys when you mean full identity
- Don't skip indexes on lookup properties
- Don't run multi-statement mutations without a transaction

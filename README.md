docker compose up -d # start everything in background
docker compose ps # see what's running
docker compose logs -f neo4j # tail Neo4j logs (Ctrl+C to stop tailing)
docker compose stop # stop containers (data preserved)
docker compose start # start them again
docker compose down # stop AND remove containers (data still preserved in volume)
docker compose down -v # ⚠️ also deletes volumes — wipes all your graph data

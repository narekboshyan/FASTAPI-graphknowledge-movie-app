import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from db import driver
from logger import logger
from routers import movies, people, relationships, seed

app = FastAPI(title="Movie KG API", version="0.1.0")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        logger.exception(
            f"[error]✗ {request.method} {request.url.path}[/] "
            f"[error]500[/] [dim]{elapsed:.1f}ms[/] — {e}"
        )
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    elapsed = (time.perf_counter() - start) * 1000
    status = response.status_code
    if status < 400:
        style, icon = "success", "✓"
    elif status < 500:
        style, icon = "warning", "⚠"
    else:
        style, icon = "error", "✗"

    logger.info(
        f"[{style}]{icon} {request.method}[/] {request.url.path} "
        f"[{style}]{status}[/] [dim]{elapsed:.1f}ms[/]"
    )
    return response


app.include_router(movies.router)
app.include_router(people.router)
app.include_router(relationships.router)
app.include_router(seed.router)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.on_event("startup")
def startup():
    logger.info("[success]✓ Movie KG API started[/]")


@app.on_event("shutdown")
def shutdown():
    logger.warning("[warning]⚠ Shutting down Neo4j driver[/]")
    driver.close()

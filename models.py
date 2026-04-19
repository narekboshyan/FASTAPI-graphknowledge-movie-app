from pydantic import BaseModel


class Movie(BaseModel):
    title: str
    year: int
    genre: str


class Person(BaseModel):
    name: str
    born: int | None = None

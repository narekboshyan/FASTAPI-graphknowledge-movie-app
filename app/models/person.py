from pydantic import BaseModel


class Person(BaseModel):
    name: str
    born: int | None = None

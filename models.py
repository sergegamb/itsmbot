from pydantic import BaseModel


class Status(BaseModel):
    name: str

class Ticket(BaseModel):
    id: int
    subject: str
    description: str | None = None
    status: Status
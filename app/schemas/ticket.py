from pydantic import BaseModel


class TicketRequest(BaseModel):
    ticket: str
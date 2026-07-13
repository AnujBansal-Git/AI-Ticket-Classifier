from pydantic import BaseModel


class TicketRequest(BaseModel):
    ticket: str


class TicketResponse(BaseModel):
    id: int
    ticket: str
    category: str
    priority: str
    suggested_team: str
    summary: str
    sentiment: str

    model_config = {
        "from_attributes": True
    }
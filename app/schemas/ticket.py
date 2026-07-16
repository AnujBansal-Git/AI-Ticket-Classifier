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

class TicketCreatedResponse(BaseModel):
    id: int
    status: str
    message: str


class UnclassifiedTicketResponse(BaseModel):
    id: int
    status: str
    message: str
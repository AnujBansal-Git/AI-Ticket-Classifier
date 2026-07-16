from pydantic import BaseModel


class UnclassifiedTicketResponse(BaseModel):
    id: int
    ticket: str
    source: str
    bulk_job_id: int | None

    model_config = {
        "from_attributes": True
    }
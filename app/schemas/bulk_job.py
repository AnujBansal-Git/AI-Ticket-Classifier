from pydantic import BaseModel

from app.schemas.ticket import TicketResponse
from app.schemas.unclassified_ticket import UnclassifiedTicketResponse
class BulkJobCreatedResponse(BaseModel):
    bulk_job_id: int
    message: str
class BulkJobResponse(BaseModel):
    id: int
    filename: str
    status: str

    total_tickets: int
    processed_tickets: int

    classified_tickets_count: int
    unclassified_tickets_count: int

    classified_tickets: list[TicketResponse]
    unclassified_tickets: list[UnclassifiedTicketResponse]
    model_config = {
        "from_attributes": True
    }
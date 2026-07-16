from pydantic import BaseModel


class BulkJobCreatedResponse(BaseModel):
    bulk_job_id: int
    message: str


class BulkJobResponse(BaseModel):
    id: int
    filename: str
    status: str

    total_tickets: int
    processed_tickets: int
    classified_tickets: int
    unclassified_tickets: int

    model_config = {
        "from_attributes": True
    }
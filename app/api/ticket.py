from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketRequest

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post("/classify")
def classify_ticket(
    request: TicketRequest,
    db: Session = Depends(get_db),
):
    ticket = Ticket(
        ticket=request.ticket
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return {
        "id": ticket.id,
        "ticket": ticket.ticket
    }

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "id": ticket.id,
        "ticket": ticket.ticket
    }
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.db.database import Base, engine
from app.db.session import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import TicketRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {
        "message": "AI Ticket Classifier API"
    }


@app.post("/tickets/classify")
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
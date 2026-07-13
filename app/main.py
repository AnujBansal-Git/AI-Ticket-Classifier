from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.ml.predict import predict
from app.models.ticket import Ticket
from app.schemas.ticket import TicketRequest, TicketResponse
from app.services.post_processor import post_process
from app.services.sentiment import analyze_sentiment
from app.services.summary import generate_summary

from app.db.database import Base, engine
from app.models.ticket import Ticket

app = FastAPI(title="AI Ticket Classifier API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "AI Ticket Classifier API is running."}


@app.post("/tickets/classify", response_model=TicketResponse)
def classify_ticket(
    request: TicketRequest,
    db: Session = Depends(get_db),
):

    category = predict(request.ticket, "category")
    priority = predict(request.ticket, "priority")
    team = predict(request.ticket, "team")

    summary = generate_summary(request.ticket)
    sentiment = analyze_sentiment(request.ticket)

    category, priority, team = post_process(
        request.ticket,
        category,
        priority,
        team,
    )

    ticket = Ticket(
        ticket=request.ticket,
        category=category,
        priority=priority,
        suggested_team=team,
        summary=summary,
        sentiment=sentiment,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):

    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    return ticket
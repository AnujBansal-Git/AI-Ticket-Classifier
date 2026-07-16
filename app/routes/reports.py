from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ticket import Ticket

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/category-summary")
def category_summary(
    db: Session = Depends(get_db),
):

    total_tickets = db.query(Ticket).count()

    category_counts = (
        db.query(
            Ticket.category,
            func.count(Ticket.id).label("count"),
        )
        .group_by(Ticket.category)
        .all()
    )

    priority_counts = (
        db.query(
            Ticket.priority,
            func.count(Ticket.id).label("count"),
        )
        .group_by(Ticket.priority)
        .all()
    )

    sentiment_counts = (
        db.query(
            Ticket.sentiment,
            func.count(Ticket.id).label("count"),
        )
        .group_by(Ticket.sentiment)
        .all()
    )

    return {
        "total_tickets": total_tickets,
        "categories": [
            {
                "category": category,
                "count": count,
            }
            for category, count in category_counts
        ],
        "priorities": [
            {
                "priority": priority,
                "count": count,
            }
            for priority, count in priority_counts
        ],
        "sentiments": [
            {
                "sentiment": sentiment,
                "count": count,
            }
            for sentiment, count in sentiment_counts
        ],
    }
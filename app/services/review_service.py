from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.training_feedback import TrainingFeedback
from app.models.unclassified_ticket import UnclassifiedTicket
from app.services.sentiment import analyze_sentiment
from app.services.summary import generate_summary


def review_ticket(
    db: Session,
    unclassified_ticket: UnclassifiedTicket,
    category: str,
    priority: str,
    team: str,
):
    """
    Convert an unclassified ticket into a classified ticket
    and store it for future retraining.
    """

    ticket = Ticket(
        ticket=unclassified_ticket.ticket,
        category=category,
        priority=priority,
        suggested_team=team,
        summary=generate_summary(unclassified_ticket.ticket),
        sentiment=analyze_sentiment(unclassified_ticket.ticket),
        user_id=unclassified_ticket.user_id,
        bulk_job_id=unclassified_ticket.bulk_job_id,
    )

    feedback = TrainingFeedback(
        ticket=unclassified_ticket.ticket,
        category=category,
        priority=priority,
        team=team,
        user_id=unclassified_ticket.user_id,
    )

    db.add(ticket)
    db.add(feedback)
    db.delete(unclassified_ticket)

    return ticket
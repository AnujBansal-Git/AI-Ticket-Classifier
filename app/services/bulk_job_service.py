import pandas as pd
from sqlalchemy.orm import Session

from app.ml.predict import predict
from app.models.bulk_job import BulkJob
from app.models.ticket import Ticket
from app.models.unclassified_ticket import UnclassifiedTicket
from app.models.user import User
from app.services.classification_validator import is_classifiable
from app.services.post_processor import post_process
from app.services.summary import generate_summary
from app.services.sentiment import analyze_sentiment

def create_bulk_job(
    db: Session,
    current_user: User,
    filename: str,
    total_tickets: int,
) -> BulkJob:
    """
    Create a bulk job before sending it to the background worker.
    """

    job = BulkJob(
        filename=filename,
        status="queued",
        total_tickets=total_tickets,
        processed_tickets=0,
        classified_tickets=0,
        unclassified_tickets=0,
        user_id=current_user.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def process_bulk_job(
    db: Session,
    job: BulkJob,
    dataframe: pd.DataFrame,
):
    """
    Process an existing bulk job in the background.
    """

    job.status = "processing"
    db.commit()

    for ticket_text in dataframe["ticket"]:

        ticket_text = str(ticket_text).strip()

        if not is_classifiable(ticket_text):

            unclassified_ticket = UnclassifiedTicket(
                ticket=ticket_text,
                source="bulk",
                user_id=job.user_id,
                bulk_job_id=job.id,
            )

            db.add(unclassified_ticket)

            job.processed_tickets += 1
            job.unclassified_tickets += 1

            db.commit()

            continue

        category = predict(ticket_text, "category")
        priority = predict(ticket_text, "priority")
        team = predict(ticket_text, "team")

        summary = generate_summary(ticket_text)

        sentiment = analyze_sentiment(ticket_text)

        category, priority, team = post_process(
            ticket_text,
            category,
            priority,
            team,
        )

        ticket = Ticket(
            ticket=ticket_text,
            category=category,
            priority=priority,
            suggested_team=team,
            summary=summary,
            sentiment=sentiment,
            bulk_job_id=job.id,
            user_id=job.user_id,
        )

        db.add(ticket)

        job.processed_tickets += 1
        job.classified_tickets += 1

        db.commit()

    job.status = "completed"

    db.commit()

    return job
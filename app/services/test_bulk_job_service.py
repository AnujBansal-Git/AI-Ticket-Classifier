import pandas as pd

from app.db.session import SessionLocal
from app.models.bulk_job import BulkJob
from app.models.ticket import Ticket
from app.services.bulk_job_service import process_bulk_job


def main():

    db = SessionLocal()

    df = pd.DataFrame(
        {
            "ticket": [
                "My laptop crashes every few minutes.",
                "I was charged twice for my subscription.",
                "Thank you for resolving my issue."
            ]
        }
    )

    job = process_bulk_job(
        db=db,
        filename="test.csv",
        dataframe=df,
    )

    print("=" * 60)
    print("BULK JOB")
    print("=" * 60)

    print(job.id)
    print(job.status)
    print(job.total_tickets)

    print()

    print("=" * 60)
    print("TICKETS")
    print("=" * 60)

    tickets = (
        db.query(Ticket)
        .filter(Ticket.bulk_job_id == job.id)
        .all()
    )

    for ticket in tickets:
        print(ticket.id)
        print(ticket.ticket)
        print(ticket.category)
        print(ticket.bulk_job_id)
        print("-" * 40)

    db.close()


if __name__ == "__main__":
    main()
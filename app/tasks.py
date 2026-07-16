from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.bulk_job import BulkJob
from app.services.bulk_job_service import process_bulk_job

import pandas as pd


@celery_app.task
def process_bulk_job_task(
    job_id: int,
    tickets: list[str],
):
    """
    Background task for bulk ticket classification.
    """

    db = SessionLocal()

    try:

        job = (
            db.query(BulkJob)
            .filter(BulkJob.id == job_id)
            .first()
        )

        if job is None:
            return

        dataframe = pd.DataFrame(
            {"ticket": tickets}
        )

        process_bulk_job(
            db=db,
            job=job,
            dataframe=dataframe,
        )

    finally:
        db.close()
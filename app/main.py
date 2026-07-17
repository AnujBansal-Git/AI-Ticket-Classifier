import pandas as pd
import pandas.errors
from typing import Union

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.ml.predict import predict
from app.models.ticket import Ticket
from app.models.unclassified_ticket import UnclassifiedTicket
from app.models.user import User
from app.routes.auth import router as auth_router
from app.routes.reports import router as reports_router
from app.schemas.bulk_job import (
    BulkJobCreatedResponse,
    BulkJobResponse,
)
from app.schemas.ticket import (
    TicketCreatedResponse,
    TicketRequest,
    TicketResponse,
    UnclassifiedTicketResponse,
)
from app.services.bulk_job_service import (
    create_bulk_job,
)
from app.tasks import process_bulk_job_task
from app.services.classification_validator import is_classifiable
from app.services.post_processor import post_process
from app.services.sentiment import analyze_sentiment
from app.services.summary import generate_summary
from app.schemas.review import (
    ReviewRequest,
    ReviewResponse,
    BulkReviewItem,
)
from app.models.training_feedback import TrainingFeedback
from app.models.bulk_job import BulkJob

from app.schemas.unclassified_ticket import (
    UnclassifiedTicketResponse as UnclassifiedTicketDBResponse,
)

from app.services.review_service import review_ticket

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter

from app.exceptions.custom_exceptions import AppException
from app.exceptions.handlers import app_exception_handler

from app.exceptions.custom_exceptions import CSVError

from app.core.logging import setup_logging
from app.middleware.request_logging import request_logging_middleware

app = FastAPI(
    title="AI Ticket Classifier API",
    description="AI-powered ticket classification system",
    version="1.0.0",
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.include_router(auth_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {"message": "AI Ticket Classifier API is running."}


@app.post(
    "/tickets/classify",
    response_model=Union[
        TicketCreatedResponse,
        UnclassifiedTicketResponse,
    ],
)
def classify_ticket(
    request: TicketRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not is_classifiable(request.ticket):

        unclassified_ticket = UnclassifiedTicket(
            ticket=request.ticket,
            source="single",
            user_id=current_user.id,
        )

        db.add(unclassified_ticket)
        db.commit()
        db.refresh(unclassified_ticket)

        return UnclassifiedTicketResponse(
            id=unclassified_ticket.id,
            status="unclassified",
            message=(
                "The ticket could not be classified. "
                "Please provide more details or classify it manually."
            ),
        )

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
        user_id=current_user.id,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return TicketCreatedResponse(
        id=ticket.id,
        status="classified",
        message="Ticket classified successfully.",
    )

@app.post( "/unclassified-tickets/{ticket_id}/review",
    response_model=ReviewResponse,
)
def review_unclassified_ticket(
    ticket_id: int,
    request: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    unclassified_ticket = (
        db.query(UnclassifiedTicket)
        .filter(
            UnclassifiedTicket.id == ticket_id,
            UnclassifiedTicket.user_id == current_user.id,
        )
        .first()
    )

    if unclassified_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Unclassified ticket not found.",
        )

    ticket = review_ticket(
        db=db,
        unclassified_ticket=unclassified_ticket,
        category=request.category,
        priority=request.priority,
        team=request.team,
    )

    db.commit()
    db.refresh(ticket)

    return ReviewResponse(
        message="Ticket reviewed successfully.",
        ticket_id=ticket.id,
    )

@app.post("/bulk-jobs/{job_id}/review")
def review_bulk_job(
    job_id: int,
    requests: list[BulkReviewItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reviewed = 0

    for request in requests:

        unclassified_ticket = (
            db.query(UnclassifiedTicket)
            .filter(
                UnclassifiedTicket.id == request.ticket_id,
                UnclassifiedTicket.bulk_job_id == job_id,
                UnclassifiedTicket.user_id == current_user.id,
            )
            .first()
        )

        if unclassified_ticket is None:
          continue

        review_ticket(
             db=db,
             unclassified_ticket=unclassified_ticket,
             category=request.category,
             priority=request.priority,
             team=request.team,
        )

        reviewed += 1
    
    db.commit()

    return {
       "message": f"{reviewed} ticket(s) reviewed successfully."
    }   

@app.get(
    "/tickets",
    response_model=Union[
        TicketResponse,
        list[TicketResponse],
    ],
)
def get_tickets(
    ticket_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
    )

    if ticket_id is not None:

        ticket = (
            query
            .filter(Ticket.id == ticket_id)
            .first()
        )

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found.",
            )

        return ticket

    return (
        query
        .order_by(Ticket.id.desc())
        .all()
    )

@app.post(
    "/bulk-jobs",
    response_model=BulkJobCreatedResponse,
)
async def create_bulk_job_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not file.filename.endswith(".csv"):
        raise CSVError(
           code="INVALID_FILE_TYPE",
           message="Please upload a CSV file.",
           status_code=400,
        )

    try:
       df = pd.read_csv(file.file)
    except (pd.errors.ParserError, UnicodeDecodeError, pd.errors.EmptyDataError):
         raise CSVError(
            code="INVALID_CSV",
            message="The uploaded CSV file could not be read.",
            status_code=400,
        )

    if "ticket" not in df.columns:
        raise CSVError(
            code="MISSING_TICKET_COLUMN",
            message="CSV must contain a 'ticket' column.",
            status_code=400,
        )

    job = create_bulk_job(
    db=db,
    current_user=current_user,
    filename=file.filename,
    total_tickets=len(df),
    )

    process_bulk_job_task.delay(
        job.id,
        df["ticket"].tolist(),
    )

    return BulkJobCreatedResponse(
        bulk_job_id=job.id,
        message=(
           "Bulk job created successfully. "
           "Processing has started in the background."
    ),
)

@app.get(
    "/bulk-jobs/{job_id}",
    response_model=BulkJobResponse,
)
def get_bulk_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    job = (
        db.query(BulkJob)
        .filter(
            BulkJob.id == job_id,
            BulkJob.user_id == current_user.id,
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Bulk job not found.",
        )

    return job

@app.get(
    "/bulk-jobs/{job_id}/tickets",
    response_model=list[TicketResponse],
)
def get_bulk_job_tickets(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(Ticket)
        .filter(
            Ticket.bulk_job_id == job_id,
            Ticket.user_id == current_user.id,
        )
        .order_by(Ticket.id)
        .all()
    )

@app.get(
    "/bulk-jobs/{job_id}/unclassified-tickets",
    response_model=list[UnclassifiedTicketDBResponse],
)
def get_bulk_job_unclassified_tickets(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(UnclassifiedTicket)
        .filter(
            UnclassifiedTicket.bulk_job_id == job_id,
            UnclassifiedTicket.user_id == current_user.id,
        )
        .order_by(UnclassifiedTicket.id)
        .all()
    )
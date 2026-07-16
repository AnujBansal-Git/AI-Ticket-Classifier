from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class UnclassifiedTicket(Base):
    __tablename__ = "unclassified_tickets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    ticket: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    bulk_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("bulk_jobs.id"),
        nullable=True,
    )
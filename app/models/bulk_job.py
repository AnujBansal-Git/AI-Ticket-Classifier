from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class BulkJob(Base):
    __tablename__ = "bulk_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    filename: Mapped[str] = mapped_column(String)

    status: Mapped[str] = mapped_column(
        String,
        default="processing",
    )

    total_tickets: Mapped[int] = mapped_column(Integer)

    processed_tickets: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    classified_tickets: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    unclassified_tickets: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
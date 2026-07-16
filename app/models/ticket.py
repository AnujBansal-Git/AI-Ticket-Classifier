from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base

from sqlalchemy import ForeignKey
from sqlalchemy import Boolean
class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    ticket: Mapped[str] = mapped_column(String, nullable=False)

    category: Mapped[str] = mapped_column(String, nullable=False)

    priority: Mapped[str] = mapped_column(String, nullable=False)

    suggested_team: Mapped[str] = mapped_column(String, nullable=False)

    summary: Mapped[str] = mapped_column(String, nullable=False)

    sentiment: Mapped[str] = mapped_column(String, nullable=False)

    bulk_job_id: Mapped[int | None] = mapped_column(
    ForeignKey("bulk_jobs.id"),
    nullable=True,
)
    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False,
)
from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.database import Base


class TrainingFeedback(Base):
    __tablename__ = "training_feedback"

    id = Column(Integer, primary_key=True, index=True)

    ticket = Column(String, nullable=False)

    category = Column(String, nullable=False)

    priority = Column(String, nullable=False)

    team = Column(String, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
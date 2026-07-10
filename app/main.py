from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.ticket import router as ticket_router
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(ticket_router)


@app.get("/")
def root():
    return {
        "message": "AI Ticket Classifier API"
    }
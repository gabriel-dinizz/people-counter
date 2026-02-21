from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.detector import PeopleDetector


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.detector = PeopleDetector()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)

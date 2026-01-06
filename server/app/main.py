from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.models import router as model_router

app = FastAPI()

app.include_router(health_router)
app.include_router(model_router)
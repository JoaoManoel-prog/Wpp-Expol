from fastapi import FastAPI
from .database import Base, engine
from .models import *
from .routes.webhook import router as webhook_router
from .routes.auth import router as auth_router
from .routes.messages import router as messages_router
from .routes.tickets import router as tickets_router

app = FastAPI(title="Exata WhatsApp Support - MVP")

# Cria as tabelas (para MVP). Em prod, usar Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(webhook_router)
app.include_router(auth_router)
app.include_router(messages_router)
app.include_router(tickets_router)

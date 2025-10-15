import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import requests

# Worker simples consumindo Outbox
from app.config import settings
from app.models import Outbox
from app.services.whatsapp import send_text

engine = create_engine(settings.DATABASE_URL, echo=False, future=True, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def run():
    while True:
        with SessionLocal() as db:
            item = db.query(Outbox).filter(Outbox.status=="pending").order_by(Outbox.id.asc()).first()
            if not item:
                time.sleep(1)
                continue
            try:
                send_text(item.to_number, item.body)
                item.status = "sent"
                db.add(item); db.commit()
            except Exception as e:
                item.status = "error"
                item.error_msg = str(e)
                db.add(item); db.commit()
                time.sleep(1)

if __name__ == "__main__":
    print("Worker iniciado...")
    run()

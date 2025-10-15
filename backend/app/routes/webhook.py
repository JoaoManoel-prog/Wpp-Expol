import json
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Contact, Ticket, Message, TicketEvent
from ..utils.security import verify_meta_signature

router = APIRouter(tags=["webhook"])

@router.get("/healthz")
def healthz():
    return {"ok": True}

@router.get("/readyz")
def readyz():
    return {"ready": True}

@router.get("/webhook")
def verify_webhook(mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    # Para compatibilidade, os nomes podem vir como hub.* dependendo do proxy
    # FastAPI mapeia query params por nome; vamos aceitar ambos os formatos.
    from fastapi import Request
    # Meta envia hub.mode, hub.verify_token, hub.challenge
    # Aqui usamos nomes sem "hub." apenas por simplicidade
    if hub_verify_token != settings.VERIFY_TOKEN:
        raise HTTPException(status_code=403, detail="Verification token mismatch")
    return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge

@router.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    raw = await request.body()

    # Verificar assinatura
    signature = request.headers.get("X-Hub-Signature-256")
    ok = verify_meta_signature(settings.APP_SECRET, raw, signature)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()

    # Estrutura típica: entry -> changes -> value -> messages[]
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            for m in messages:
                msg_type = m.get("type")
                from_number = m.get("from")
                msg_id = m.get("id") or m.get("message_id")
                text_body = ""
                if msg_type == "text":
                    text_body = m.get("text", {}).get("body", "")
                elif msg_type in ("button", "interactive"):
                    # Trate conforme necessário
                    text_body = json.dumps(m)

                if not from_number or not msg_id:
                    continue

                # upsert contact
                contact = db.query(Contact).filter(Contact.wa_number == from_number).first()
                if not contact:
                    contact = Contact(wa_number=from_number)
                    db.add(contact); db.commit(); db.refresh(contact)

                # find or create open ticket
                ticket = db.query(Ticket).filter(Ticket.contact_id == contact.id, Ticket.status != "resolvido").first()
                if not ticket:
                    ticket = Ticket(contact_id=contact.id, status="aberto")
                    db.add(ticket); db.commit(); db.refresh(ticket)

                # idempotência por message_external_id
                exists = db.query(Message).filter(Message.message_external_id == msg_id).first()
                if exists:
                    continue

                # store inbound message
                body = text_body or "[unsupported-message]"
                msg = Message(ticket_id=ticket.id, user_id=None, direction="inbound", body=body, message_external_id=msg_id)
                db.add(msg)

                # evento de reopen se estava pendente
                if ticket.status == "pendente":
                    db.add(TicketEvent(ticket_id=ticket.id, type="REOPEN", meta_json="{}"))
                    ticket.status = "aberto"
                    db.add(ticket)

                db.commit()

    return {"status": "ok"}

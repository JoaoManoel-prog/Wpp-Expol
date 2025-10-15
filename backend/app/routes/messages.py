from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import SendMessageRequest
from ..models import Ticket, Message, Contact, User, Outbox
from ..config import settings

router = APIRouter(prefix="/api/messages", tags=["messages"])

def _find_contact_ticket(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    contact = db.query(Contact).filter(Contact.id == ticket.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact, ticket

@router.post("/send")
def send_message(req: SendMessageRequest, db: Session = Depends(get_db)):
    contact, ticket = _find_contact_ticket(db, req.ticket_id)

    # Assinatura com o nome do atendente (se houver)
    agent_name = ticket.current_user.name if ticket.current_user else "ATENDENTE"
    body = f"*{agent_name}*\n{req.text}"

    # Insere na outbox para o worker enviar (resiliente)
    out = Outbox(to_number=contact.wa_number, body=body, status="pending")
    db.add(out); db.commit()

    # Armazena mensagem outbound no histórico
    msg = Message(ticket_id=ticket.id, user_id=ticket.current_user_id, direction="outbound", body=body)
    db.add(msg); db.commit()

    return {"status": "queued", "outbox_id": out.id}

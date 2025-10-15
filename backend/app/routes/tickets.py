from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Ticket, User, TicketEvent, Contact, Message
from ..schemas import AssignRequest, StatusRequest

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("/{ticket_id}/assign")
def assign(ticket_id: int, req: AssignRequest, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old = ticket.current_user
    ticket.current_user_id = user.id
    db.add(ticket)
    db.add(TicketEvent(ticket_id=ticket.id, type="ASSIGN", meta_json=f'{{"from":"{old.name if old else ""}","to":"{user.name}"}}'))
    db.commit()
    return {"status":"ok"}

@router.post("/{ticket_id}/status")
def set_status(ticket_id: int, req: StatusRequest, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = req.status
    db.add(ticket)
    db.add(TicketEvent(ticket_id=ticket.id, type="STATUS", meta_json=f'{{"status":"{req.status}"}}'))
    db.commit()
    return {"status":"ok"}

@router.get("/inbox")
def inbox(db: Session = Depends(get_db)):
    # lista tickets com últimas mensagens e responsável
    tickets = db.query(Ticket).all()
    out = []
    for t in tickets:
        last_msg = db.query(Message).filter(Message.ticket_id==t.id).order_by(Message.id.desc()).first()
        out.append({
            "ticket_id": t.id,
            "contact": db.query(Contact).filter(Contact.id==t.contact_id).first().wa_number,
            "status": t.status,
            "responsavel": t.current_user.name if t.current_user else None,
            "last_message": last_msg.body if last_msg else None
        })
    return out

@router.get("/{ticket_id}")
def ticket_detail(ticket_id: int, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id==ticket_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    msgs = db.query(Message).filter(Message.ticket_id==t.id).order_by(Message.id.asc()).all()
    return {
        "ticket": {"id": t.id, "status": t.status, "responsavel": t.current_user.name if t.current_user else None},
        "messages": [{"direction": m.direction, "body": m.body, "created_at": str(m.created_at)} for m in msgs]
    }

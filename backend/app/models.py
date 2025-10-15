from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="agent")
    active = Column(Integer, default=1)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=True)
    wa_number = Column(String(32), unique=True, nullable=False)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    current_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="aberto")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    contact = relationship("Contact")
    current_user = relationship("User")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null para inbound
    direction = Column(String(10), nullable=False)  # inbound/outbound
    body = Column(Text, nullable=False)
    message_external_id = Column(String(128), nullable=True)  # id da Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket")
    user = relationship("User")

    __table_args__ = (UniqueConstraint("message_external_id", name="uq_message_external_id"),)

class TicketEvent(Base):
    __tablename__ = "ticket_events"
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    type = Column(String(32), nullable=False)
    meta_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Outbox(Base):
    __tablename__ = "outbox"
    id = Column(Integer, primary_key=True)
    to_number = Column(String(32), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, error
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

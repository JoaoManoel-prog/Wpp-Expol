from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class SendMessageRequest(BaseModel):
    ticket_id: int
    text: str

class AssignRequest(BaseModel):
    user_id: int

class StatusRequest(BaseModel):
    status: str

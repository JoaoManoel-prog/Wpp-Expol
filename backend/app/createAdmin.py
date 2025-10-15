from app.database import SessionLocal, Base, engine
from app.models import User
from passlib.hash import bcrypt

# Cria as tabelas se ainda não existirem
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Criação do usuário administrador
admin = User(
    name="Joao Manoel",
    email="admin@exata.com",
    password_hash=bcrypt.hash("e@p.4100"),
    role="admin"
)

db.add(admin)
db.commit()
db.close()

print("✅ Usuário administrador criado com sucesso!")

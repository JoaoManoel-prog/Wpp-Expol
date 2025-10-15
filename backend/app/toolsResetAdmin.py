import argparse
from passlib.hash import bcrypt  # se preferir, veja a nota PBKDF2 abaixo
from app.database import SessionLocal, Base, engine
from app.models import User

def upsert_admin(email: str, name: str, password: str):
    Base.metadata.create_all(bind=engine)  # garante tabelas
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.name = name
            user.password_hash = bcrypt.hash(password)
            user.role = "admin"
            print(f"🔁 Atualizando admin: {email}")
        else:
            user = User(
                name=name,
                email=email,
                password_hash=bcrypt.hash(password),
                role="admin",
                active=1
            )
            db.add(user)
            print(f"✅ Criando admin: {email}")
        db.commit()
    finally:
        db.close()
    print("✔️  Pronto.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--email", required=True)
    p.add_argument("--name", default="Administrador")
    p.add_argument("--password", required=True)
    args = p.parse_args()
    upsert_admin(args.email, args.name, args.password)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db, AdminUser
from ..auth import verify_password, create_access_token, hash_password
from ..config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali non valide",
        )
    token = create_access_token({"sub": admin.username})
    return TokenResponse(access_token=token)


@router.post("/setup", include_in_schema=False)
def setup_admin(db: Session = Depends(get_db)):
    existing = db.query(AdminUser).filter(AdminUser.username == settings.ADMIN_USERNAME).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin già configurato")
    admin = AdminUser(
        username=settings.ADMIN_USERNAME,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
    )
    db.add(admin)
    db.commit()
    return {"message": f"Admin '{settings.ADMIN_USERNAME}' creato con successo"}
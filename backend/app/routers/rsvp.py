from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from ..database import get_db, Guest, RSVPResponse
from ..config import settings

router = APIRouter()


class CompanionDetail(BaseModel):
    nome: str
    cognome: str
    tipo: str = "adulto"  # "adulto" o "bambino"

class RSVPSubmit(BaseModel):
    attending: bool
    companions: int = Field(default=0, ge=0, le=20)
    companions_details: Optional[list[CompanionDetail]] = None
    menu_choice: Optional[str] = Field(default=None, pattern="^(standard|vegetarian|vegan|gluten_free)$")
    allergies: Optional[str] = Field(default=None, max_length=300)
    message: Optional[str] = Field(default=None, max_length=500)


class GuestInfo(BaseModel):
    name: str
    has_responded: bool
    attending: Optional[bool] = None
    couple_name: str
    wedding_date: str
    wedding_location: str


@router.get("/{token}", response_model=GuestInfo)
def get_guest_info(token: str, db: Session = Depends(get_db)):
    """Restituisce info sull'invitato tramite token. Usato per popolare la pagina RSVP."""
    guest = db.query(Guest).filter(Guest.token == token).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Invito non trovato")

    return GuestInfo(
        name=guest.name,
        has_responded=guest.response is not None,
        attending=guest.response.attending if guest.response else None,
        couple_name=settings.COUPLE_NAME,
        wedding_date=settings.WEDDING_DATE,
        wedding_location=settings.WEDDING_LOCATION,
    )


@router.post("/{token}")
def submit_rsvp(token: str, data: RSVPSubmit, db: Session = Depends(get_db)):
    """Registra la risposta RSVP dell'invitato. Non modificabile dopo il submit."""
    guest = db.query(Guest).filter(Guest.token == token).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Invito non trovato")

    if guest.response is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hai già risposto. Non è possibile modificare la risposta.",
        )

    import json

    response = RSVPResponse(
        guest_id=guest.id,
        attending=data.attending,
        companions=data.companions if data.attending else 0,
        companions_details=json.dumps([c.dict() for c in data.companions_details]) if data.companions_details else None,
        menu_choice=data.menu_choice if data.attending else None,
        allergies=data.allergies,
        message=data.message,
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    return {
        "message": "Risposta registrata con successo. Grazie!",
        "attending": response.attending,
        "guest_name": guest.name,
    }

import secrets
import csv
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from ..database import get_db, Guest, RSVPResponse
from ..auth import get_current_admin

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class GuestCreate(BaseModel):
    name: str
    email: Optional[str] = None


class GuestOut(BaseModel):
    id: int
    name: str
    email: Optional[str]
    token: str
    has_responded: bool
    attending: Optional[bool]
    companions: Optional[int]
    companions_details: Optional[str]
    menu_choice: Optional[str]
    allergies: Optional[str]
    message: Optional[str]
    submitted_at: Optional[str]

    class Config:
        from_attributes = True


class StatsOut(BaseModel):
    total_guests: int
    responded: int
    attending: int
    not_attending: int
    pending: int
    total_companions: int
    menu_standard: int
    menu_vegetarian: int
    menu_vegan: int
    menu_gluten_free: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/guests", response_model=List[GuestOut])
def list_guests(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    guests = db.query(Guest).all()
    result = []
    for g in guests:
        r = g.response
        result.append(GuestOut(
            id=g.id,
            name=g.name,
            email=g.email,
            token=g.token,
            has_responded=r is not None,
            attending=r.attending if r else None,
            companions=r.companions if r else None,
            menu_choice=r.menu_choice if r else None,
            message=r.message if r else None,
            submitted_at=str(r.submitted_at) if r else None,
            allergies=r.allergies if r else None,
            companions_details=r.companions_details if r else None,
        ))
    return result


@router.post("/guests", response_model=GuestOut)
def create_guest(data: GuestCreate, db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    token = "tok_" + secrets.token_urlsafe(32)
    guest = Guest(name=data.name, email=data.email, token=token)
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return GuestOut(
        id=guest.id, name=guest.name, email=guest.email,
        token=guest.token, has_responded=False,
        attending=None, companions=None, menu_choice=None,
        message=None, submitted_at=None,
    )


@router.delete("/guests/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Invitato non trovato")
    # Elimina prima la risposta se esiste
    if guest.response:
        db.delete(guest.response)
        db.flush()
    db.delete(guest)
    db.commit()
    return {"message": "Invitato eliminato"}


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    guests = db.query(Guest).all()
    responses = db.query(RSVPResponse).all()

    attending_responses = [r for r in responses if r.attending]
    not_attending = [r for r in responses if not r.attending]

    return StatsOut(
        total_guests=len(guests),
        responded=len(responses),
        attending=len(attending_responses),
        not_attending=len(not_attending),
        pending=len(guests) - len(responses),
        total_companions=sum(r.companions or 0 for r in attending_responses),
        menu_standard=sum(1 for r in attending_responses if r.menu_choice == "standard"),
        menu_vegetarian=sum(1 for r in attending_responses if r.menu_choice == "vegetarian"),
        menu_vegan=sum(1 for r in attending_responses if r.menu_choice == "vegan"),
        menu_gluten_free=sum(1 for r in attending_responses if r.menu_choice == "gluten_free"),
    )


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db), _: str = Depends(get_current_admin)):
    guests = db.query(Guest).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nome", "Email", "Token", "Risposta", "Accompagnatori", "Menu", "Messaggio", "Data risposta"])
    for g in guests:
        r = g.response
        writer.writerow([
            g.name, g.email or "", g.token,
            ("Presente" if r.attending else "Assente") if r else "In attesa",
            r.companions if r else "",
            r.menu_choice if r else "",
            r.message if r else "",
            str(r.submitted_at) if r else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=invitati.csv"},
    )

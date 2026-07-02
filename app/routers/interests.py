import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user
from app.services.email_service import send_notification_email
from app.schemas import InterestStatusEnum

router = APIRouter(prefix="/interests", tags=["Interests & Requests Flow"])

@router.post("/express", status_code=status.HTTP_201_CREATED)
def express_interest(listing_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.Role.TENANT:
        raise HTTPException(status_code=403, detail="Only tenants can express booking interest.")
    
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Target room listing not found.")

    existing_interest = db.query(models.InterestMatch).filter(
        models.InterestMatch.listing_id == listing_id,
        models.InterestMatch.tenant_id == current_user.id
    ).first()
    if existing_interest:
        return {"status": "Interest state already registered.", "id": existing_interest.id}

    new_interest = models.InterestMatch(
        id=str(uuid.uuid4()),
        listing_id=listing_id,
        tenant_id=current_user.id,
        status=models.RequestStatus.PENDING
    )
    db.add(new_interest)
    db.commit()

    match = db.query(models.CompatibilityMatch).filter(
        models.CompatibilityMatch.listing_id == listing_id,
        models.CompatibilityMatch.tenant_id == current_user.id
    ).first()

    score = match.score if match else 0

    if score >= 80:
        owner = db.query(models.User).filter(models.User.id == listing.owner_id).first()
        if owner:
            send_notification_email(
                recipient_email=owner.email,
                subject="🔥 High-Compatibility Room Applicant Match!",
                text_content=f"Hello {owner.name},\nA highly compatible match ({score}%) has expressed interest in your listing at {listing.location}.\n\nReview your dashboard to accept or decline."
            )

    return {"message": "Interest tracking generated successfully.", "interest_id": new_interest.id}

@router.put("/status", status_code=status.HTTP_200_OK)
def update_interest_status(
    interest_id: str, 
    status_choice: InterestStatusEnum, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.role != models.Role.OWNER:
        raise HTTPException(status_code=403, detail="Only listings owners can change request statuses.")
    
    interest = db.query(models.InterestMatch).filter(models.InterestMatch.id == interest_id).first()
    if not interest:
        raise HTTPException(status_code=404, detail="Application link tracking context missing.")
    
    listing = db.query(models.Listing).filter(models.Listing.id == interest.listing_id).first()
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ownership violation for requested state modification.")

    interest.status = status_choice.value
    db.commit()

    tenant = db.query(models.User).filter(models.User.id == interest.tenant_id).first()
    if tenant:
        send_notification_email(
            recipient_email=tenant.email,
            subject=f"Update on your flat application request for {listing.location}",
            text_content=f"Hello {tenant.name},\nThe owner has updated your interest application request status to: {status_choice.value}."
        )

    return {"message": f"Interest status successfully changed to {status_choice.value}."}
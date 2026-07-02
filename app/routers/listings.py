import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user

router = APIRouter(prefix="/listings", tags=["Owner Room Listings"])

@router.post("", response_model=schemas.ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(listing: schemas.ListingCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.Role.OWNER:
        raise HTTPException(status_code=403, detail="Only owners can create structural room listings[cite: 1].")
    
    new_listing = models.Listing(
        id=str(uuid.uuid4()),
        owner_id=current_user.id,
        location=listing.location,
        rent=listing.rent,
        available_from=listing.available_from,
        room_type=listing.room_type,
        is_furnished=listing.is_furnished,
        photos=";".join(listing.photos)
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@router.put("/{listing_id}/fill", status_code=status.HTTP_200_OK)
def mark_as_filled(listing_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Requested flat object does not exist.")
    if listing.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Action prohibited: listing ownership mismatch.")
    
    listing.is_filled = True 
    db.commit()
    return {"message": "Listing has been successfully updated to filled state[cite: 1]."}
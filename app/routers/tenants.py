import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.routers.auth import get_current_user
from app.services.ai_service import compute_compatibility

router = APIRouter(prefix="/tenants", tags=["Tenant Profiles & Discovery"])

@router.post("/profile", response_model=schemas.TenantProfileOut, status_code=status.HTTP_201_CREATED)
def create_or_update_profile(profile: schemas.TenantProfileCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.Role.TENANT:
        raise HTTPException(status_code=403, detail="Only verified tenant sub-roles can execute this route[cite: 1].")
    
    existing_profile = db.query(models.TenantProfile).filter(models.TenantProfile.tenant_id == current_user.id).first()
    if existing_profile:
        existing_profile.preferred_location = profile.preferred_location
        existing_profile.budget_min = profile.budget_min
        existing_profile.budget_max = profile.budget_max
        existing_profile.move_in_date = profile.move_in_date
        db.commit()
        db.refresh(existing_profile)
        return existing_profile

    new_profile = models.TenantProfile(
        id=str(uuid.uuid4()),
        tenant_id=current_user.id,
        preferred_location=profile.preferred_location,
        budget_min=profile.budget_min,
        budget_max=profile.budget_max,
        move_in_date=profile.move_in_date
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile

@router.get("/browse", response_model=List[schemas.ListingOut])
def browse_and_rank_listings(location: str = None, max_budget: float = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.Role.TENANT:
        raise HTTPException(status_code=403, detail="Discovery actions are bounded to tenant actors[cite: 1].")
    
    tenant_profile = db.query(models.TenantProfile).filter(models.TenantProfile.tenant_id == current_user.id).first()
    if not tenant_profile:
        raise HTTPException(status_code=400, detail="Please create your tenant searching criteria matrix profile first[cite: 1].")

    query = db.query(models.Listing).filter(models.Listing.is_filled == False)
    if location:
        query = query.filter(models.Listing.location.icontains(location))
    if max_budget:
        query = query.filter(models.Listing.rent <= max_budget)
    
    listings = query.all()
    ranked_listings = []

    for listing in listings:
        match_record = db.query(models.CompatibilityMatch).filter(
            models.CompatibilityMatch.listing_id == listing.id,
            models.CompatibilityMatch.tenant_id == current_user.id
        ).first()

        if not match_record:
            ai_res = compute_compatibility(listing, tenant_profile)
            match_record = models.CompatibilityMatch(
                id=str(uuid.uuid4()),
                listing_id=listing.id,
                tenant_id=current_user.id,
                score=ai_res["score"],
                explanation=ai_res["explanation"],
                is_fallback=ai_res.get("is_fallback", False)
            )
            db.add(match_record)
            db.commit()
            db.refresh(match_record)

        listing_data = schemas.ListingOut.from_orm(listing)
        listing_data.compatibility_score = match_record.score
        listing_data.compatibility_explanation = match_record.explanation
        ranked_listings.append(listing_data)

    ranked_listings.sort(key=lambda x: x.compatibility_score or 0, reverse=True)
    return ranked_listings
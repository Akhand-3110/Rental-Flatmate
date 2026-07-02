import enum
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Enum, Text, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Role(str, enum.Enum):
    TENANT = "tenant"
    OWNER = "owner"
    ADMIN = "admin"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.TENANT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="owner", cascade="all, delete-orphan")
    tenant_profile = relationship("TenantProfile", back_populates="tenant", uselist=False, cascade="all, delete-orphan")

class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    location = Column(String, nullable=False)
    rent = Column(Float, nullable=False)
    available_from = Column(DateTime, nullable=False)
    room_type = Column(String, nullable=False)
    is_furnished = Column(Boolean, default=False)
    photos = Column(Text, default="")
    is_filled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="listings")
    matches = relationship("CompatibilityMatch", back_populates="listing", cascade="all, delete-orphan")
    interests = relationship("InterestMatch", back_populates="listing", cascade="all, delete-orphan")

class TenantProfile(Base):
    __tablename__ = "tenant_profiles"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_location = Column(String, nullable=False)
    budget_min = Column(Float, nullable=False)
    budget_max = Column(Float, nullable=False)
    move_in_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("User", back_populates="tenant_profile")

class CompatibilityMatch(Base):
    __tablename__ = "compatibility_matches"

    id = Column(String, primary_key=True, index=True)
    listing_id = Column(String, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    is_fallback = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="matches")

class InterestMatch(Base):
    __tablename__ = "interest_matches"

    id = Column(String, primary_key=True, index=True)
    listing_id = Column(String, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="interests")
    tenant = relationship("User")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    room_key = Column(String, index=True, nullable=False) # "listing_id_tenant_id"
    sender_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
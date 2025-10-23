"""Database models for multi-tenant token management."""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    """User model representing a tenant/user in the system."""
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    oauth_tokens: Mapped[list["OAuthToken"]] = relationship("OAuthToken", back_populates="user", cascade="all, delete-orphan")
    personal_access_tokens: Mapped[list["PersonalAccessToken"]] = relationship("PersonalAccessToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class OAuthToken(Base):
    """OAuth tokens from providers like Meta (stored in plain text for now)."""
    __tablename__ = "oauth_tokens"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="meta")
    
    # Plain text storage (encryption can be added later)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="oauth_tokens")
    
    __table_args__ = (
        Index("ix_oauth_tokens_user_provider", "user_id", "provider"),
    )
    
    def __repr__(self):
        return f"<OAuthToken(id={self.id}, user_id={self.user_id}, provider={self.provider})>"


class PersonalAccessToken(Base):
    """Personal Access Tokens (PATs) for API authentication."""
    __tablename__ = "personal_access_tokens"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Token storage - prefix for quick lookup, hash for verification
    token_prefix: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    scopes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of scopes
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="personal_access_tokens")
    
    __table_args__ = (
        Index("ix_pats_token_prefix", "token_prefix"),
        Index("ix_pats_user_id", "user_id"),
    )
    
    @property
    def is_active(self) -> bool:
        """Check if token is active (not revoked and not expired)."""
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def __repr__(self):
        return f"<PersonalAccessToken(id={self.id}, name={self.name}, user_id={self.user_id})>"

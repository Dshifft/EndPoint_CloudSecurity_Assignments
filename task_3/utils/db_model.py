from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from utils.db import Base


class Admin(Base):
    """Database model for administrators."""

    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    mfa_code_hash = Column(String, nullable=True)
    mfa_code_expires_at = Column(DateTime(timezone=True), nullable=True)


class User(Base):
    """Database model for voting users."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Candidate(Base):
    """Database model for voting candidates."""

    __tablename__ = "candidates"

    candidate_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.admin_id", ondelete="SET NULL"), nullable=True)

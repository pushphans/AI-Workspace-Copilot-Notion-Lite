from sqlalchemy import ForeignKey
from pydantic import EmailStr
from ai_workspace_copilot_notion_lite.core.db import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Text, DateTime, func, Boolean
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime



class UserModel(Base):
    __tablename__ = "users"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    name : Mapped[str] = mapped_column(Text, nullable = False)
    email : Mapped[EmailStr] = mapped_column(Text, nullable = False, unique = True)
    password_hash : Mapped[str] = mapped_column(Text, nullable = False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)





class RefreshTokenModel(Base):
    __tablename__ = "refresh_token"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    user_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index = True)
    refresh_token : Mapped[str] = mapped_column(Text, unique = True)
    expires_at : Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone = True), server_default= func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)




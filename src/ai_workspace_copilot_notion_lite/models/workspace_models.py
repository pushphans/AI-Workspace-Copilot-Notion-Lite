from sqlalchemy import UniqueConstraint
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import func, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ai_workspace_copilot_notion_lite.core.db import Base
import uuid
from datetime import datetime
import enum
from sqlalchemy import Enum as SQLEnum



class WorkspaceRole(enum.Enum):
    OWNER = "owner"
    MEMBER = "member"




class WorkspaceModel(Base):
    __tablename__ = "workspaces"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    name : Mapped[str] = mapped_column(Text, nullable = False)
    description : Mapped[str | None] = mapped_column(Text, nullable = True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)



class WorkspaceMemberModel(Base):
    __tablename__ = "workspace_members"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_user",
        ),
    )

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid.uuid4)
    workspace_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable = False)
    user_id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable = False)
    role : Mapped[WorkspaceRole] = mapped_column(SQLEnum(WorkspaceRole, name = "workspace_role"), nullable = False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), nullable = False)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now(), onupdate = func.now(), nullable = False)
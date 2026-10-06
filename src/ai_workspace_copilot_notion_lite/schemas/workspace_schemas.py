from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceRole
from uuid import UUID
from datetime import datetime
from pydantic import ConfigDict
from pydantic import BaseModel, Field




class CreateWorkspaceRequestSchema(BaseModel):
    name : str = Field(...)
    description : str | None = Field(default="This is my workspace")

class CreateWorkspaceResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id : UUID
    name : str
    description : str
    created_at : datetime
    updated_at : datetime


class GetWorkspaceResponseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id : UUID
    name : str
    description : str
    created_at : datetime
    updated_at : datetime



class UpdateWorkspaceRequestSchema(BaseModel):
    name : str
    description : str | None


class UpdateWorkspaceResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id : UUID
    name : str
    description : str
    created_at : datetime
    updated_at : datetime




class CreateWorkspaceMembersRequestSchema(BaseModel):
    workspaceId  : UUID = Field(...)
    role : str = WorkspaceRole.MEMBER



class CreateWorkspaceMemberResponseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
    id : UUID
    workspace_id : UUID
    user_id : UUID
    role : str
    created_at : datetime
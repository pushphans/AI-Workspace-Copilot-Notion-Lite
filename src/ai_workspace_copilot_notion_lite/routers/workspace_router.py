from ai_workspace_copilot_notion_lite.core.security import get_user
from ai_workspace_copilot_notion_lite.models.auth_models import UserModel
from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceRole
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import UpdateWorkspaceRequestSchema
from uuid import UUID
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import UpdateWorkspaceResponseSchema
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import GetWorkspaceResponseModel
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import CreateWorkspaceResponseSchema
from fastapi import status, Query
from pydantic_core.core_schema import none_schema
from sqlalchemy import select
import uuid
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import CreateWorkspaceRequestSchema
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Depends
from ai_workspace_copilot_notion_lite.core.db import get_db
from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceModel, WorkspaceMemberModel



workspace_router = APIRouter(prefix="/workspace", tags=["WORKSPACE"])



@workspace_router.post("/create-workspace", status_code=status.HTTP_201_CREATED, response_model=CreateWorkspaceResponseSchema)
async def create_workspace(data : CreateWorkspaceRequestSchema, db : AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):

    workspace_model = WorkspaceModel(
        name = data.name,
        description = data.description
    )


    db.add(workspace_model)

    await db.flush()

    workspace_member_model = WorkspaceMemberModel(
        user_id = user.id,
        workspace_id = workspace_model.id,
        role = WorkspaceRole.OWNER
    )


    db.add(workspace_member_model)




    await db.commit()
    await db.refresh(workspace_model)

    return workspace_model

    

@workspace_router.get("/get-workspace/{id}", status_code=status.HTTP_200_OK, response_model=GetWorkspaceResponseModel)
async def get_workspace_by_id(id : UUID, db : AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):
    query = (
        select(WorkspaceModel)
        .where(WorkspaceModel.id == id)
    )

    result = await db.execute(query)

    workspace = result.scalar_one_or_none()

    if workspace is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not found"
        )

    return workspace



@workspace_router.get("/workspaces", status_code=status.HTTP_200_OK)
async def get_workspaces(
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user),
    page : int | None = Query(ge=1, default=1),
    page_size : int | None = Query(default = 10, ge=1, le=100),
    search_term : str | None = None
):

    offset = (page -1) * page_size 
    query = (
        select(WorkspaceModel)
    )


    if search_term is not None:
        query = query.where(WorkspaceModel.name.ilike(f"%{search_term}%"))


    query = query.offset(offset=offset).limit(page_size)

    result = await db.execute(query)

    workspaces = result.mappings().all()

    if not workspaces:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Not found"
        )

    return workspaces




@workspace_router.put("/update-workspace/{id}", status_code=status.HTTP_200_OK, response_model=UpdateWorkspaceResponseSchema)
async def update_workspace(id : UUID, data : UpdateWorkspaceRequestSchema, db : AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):
    query = (
        select(WorkspaceModel)
        .where(WorkspaceModel.id == id)
    )

    result = await db.execute(query)

    workspace_exists = result.scalar_one_or_none()

    if workspace_exists is None:
        raise HTTPException(
            status_code = 404,
            detail = "Not found"
        )
    
    workspace_exists.name = data.name
    workspace_exists.description = data.description

    await db.commit()
    await db.refresh(workspace_exists)

    return workspace_exists
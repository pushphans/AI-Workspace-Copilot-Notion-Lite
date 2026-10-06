import enum
from fastapi import Query
from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceModel
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from sqlalchemy import select
from ai_workspace_copilot_notion_lite.models.auth_models import UserModel
from ai_workspace_copilot_notion_lite.core.security import get_user
from uuid import UUID
from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceRole
from ai_workspace_copilot_notion_lite.schemas.workspace_schemas import CreateWorkspaceMembersRequestSchema
from ai_workspace_copilot_notion_lite.models.workspace_models import WorkspaceMemberModel
from ai_workspace_copilot_notion_lite.core.db import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from fastapi import APIRouter


wm_router = APIRouter(prefix="/workspace-members", tags=["WORKSPACE-MEMBER"])

@wm_router.post("/join-workspace", status_code=status.HTTP_201_CREATED)
async def create_workspace_members(data : CreateWorkspaceMembersRequestSchema, db: AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):
    workspace_member = WorkspaceMemberModel(
        workspace_id = data.workspaceId,
        user_id = user.id,
        role = WorkspaceRole.MEMBER
    )


    db.add(workspace_member)
    await db.commit()
    await db.refresh(workspace_member)


    return workspace_member



@wm_router.delete("/leave-workspace/{id}")
async def delete_workspace_member(id : UUID, db : AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):
    query = (
        select(WorkspaceMemberModel)
        .where(WorkspaceMemberModel.user_id == user.id)
        .where(WorkspaceMemberModel.workspace_id == id)
    )

    result = await db.execute(query)

    user_exist = result.scalar_one_or_none()

    if user_exist is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No workspace found"
        )    
    
    await db.delete(user_exist)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail" : "Workspace left successfully"}
    )



@wm_router.get("/member/workspaces")
async def get_workspaces_for_member(
    user : UserModel = Depends(get_user),
    db : AsyncSession = Depends(get_db)
):

    query = (
        select(
            WorkspaceModel.id,
            WorkspaceModel.name, 
            WorkspaceModel.description,
            WorkspaceMemberModel.role)
        .join(
            WorkspaceModel,
            WorkspaceModel.id == WorkspaceMemberModel.workspace_id
        )
        .where(WorkspaceMemberModel.user_id == user.id)
    )


    result = await db.execute(query)

    workspaces_for_member = result.mappings().all()

    if not workspaces_for_member:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No joined workspaces found"
        )

    return workspaces_for_member


@wm_router.get("/workspace/members")
async def get_workspace_members(
    workspace_id : UUID,
    db : AsyncSession = Depends(get_db),
    user : UserModel = Depends(get_user),
    page : int = Query(default=1, ge = 1),
    page_size : int = Query(default=10, le = 100),
    owner : bool = True
):      

    offset = (page - 1) * page_size
    
    query = (
        select(
            UserModel.id,
            UserModel.name,
            UserModel.email,
            WorkspaceMemberModel.role    
        )
        .join(
            WorkspaceMemberModel,
            WorkspaceMemberModel.user_id == UserModel.id   
        )
        .where(
            WorkspaceMemberModel.workspace_id == workspace_id
        )
    )


    if owner:
        query = query.where(WorkspaceMemberModel.role == WorkspaceRole.OWNER)
    else:
        query = query.where(WorkspaceMemberModel.role == WorkspaceRole.MEMBER)

    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)

    members_for_workspace = result.mappings().all()

    if not members_for_workspace:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "No members available"
        )

    return members_for_workspace
    
    

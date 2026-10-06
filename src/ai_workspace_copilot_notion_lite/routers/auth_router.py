from ai_workspace_copilot_notion_lite.core.security import get_user
from ai_workspace_copilot_notion_lite.schemas.auth_schemas import RefreshTokenResponseSchema
from ai_workspace_copilot_notion_lite.schemas.auth_schemas import RefreshTokenRequestSchema
from datetime import datetime, timezone, timedelta
from ai_workspace_copilot_notion_lite.core.config import settings
from ai_workspace_copilot_notion_lite.models.auth_models import RefreshTokenModel
from ai_workspace_copilot_notion_lite.core.security import create_refresh_token
from ai_workspace_copilot_notion_lite.core.security import create_access_token
from ai_workspace_copilot_notion_lite.core.security import verify_password
from ai_workspace_copilot_notion_lite.schemas.auth_schemas import LoginRequestSchema
from ai_workspace_copilot_notion_lite.schemas.auth_schemas import LoginResponseSchema
from sqlalchemy import select
from ai_workspace_copilot_notion_lite.core.security import hash_password
import uuid
from ai_workspace_copilot_notion_lite.models.auth_models import UserModel
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from ai_workspace_copilot_notion_lite.schemas.auth_schemas import RegisterRequestSchema
from fastapi import APIRouter, HTTPException, Depends
from ai_workspace_copilot_notion_lite.core.db import get_db
from fastapi.responses import JSONResponse



auth_router = APIRouter(prefix="/auth", tags=["AUTH"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data : RegisterRequestSchema, db : AsyncSession = Depends(get_db)):
    name = data.name
    email = data.email
    password = data.password

    if name is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Please provide the credentials"
        )

    if email is None:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Please provide the credentials"
            )

    if password is None:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Please provide the credentials"
            )

    query = (
        select(UserModel).
        where(UserModel.email == email)
    )


    result = await db.execute(query)

    users = result.scalar_one_or_none()

    if users:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Account already exists"
        )


    user : UserModel = UserModel(
        id = uuid.uuid4(),
        name  = name,
        email = email,
        password_hash = hash_password(password=password)
    )


    db.add(user)
    await db.commit()
    await db.refresh(user)


    return JSONResponse(
        status_code=201,
        content={
            "detail" : "account created successfully"
        } 
    )




@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponseSchema)
async def login(data : LoginRequestSchema, db : AsyncSession = Depends(get_db)):
    email = data.email
    password = data.password


    email_query = (
        select(UserModel)
        .where(UserModel.email == email)
    )

    email_result = await db.execute(email_query)

    email_exists = email_result.scalar_one_or_none()

    if email_exists is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid credentials"
        )

    hashed_password = email_exists.password_hash
    
    password_valid = verify_password(hashed_password=hashed_password, password=password)

    if not password_valid:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid credentials"
        )

    refresh_token_check_query = (
        select(RefreshTokenModel)
        .where(RefreshTokenModel.user_id == email_exists.id)
    )

    refresh_token_results = await db.execute(refresh_token_check_query)

    refresh_token_exists = refresh_token_results.scalar_one_or_none()

    access_token = create_access_token(user_id=email_exists.id)
                    
    refresh_token = create_refresh_token()
                    
    refresh_token_expires_on = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_IN_DAYS)

    if refresh_token_exists is None:
        refresh_token_model = RefreshTokenModel(
            id = uuid.uuid4(),
            refresh_token = refresh_token,
            user_id = email_exists.id,
            expires_at = refresh_token_expires_on,
        )
        
        db.add(refresh_token_model)
        await db.commit()
        await db.refresh(refresh_token_model)

    else:
        refresh_token_exists.refresh_token = refresh_token
        refresh_token_exists.expires_at = refresh_token_expires_on        
        
        await db.commit()

    
    return LoginResponseSchema(
        id=email_exists.id,
        name=email_exists.name,
        email=email_exists.email,
        access_token=access_token,
        access_token_expiry=settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60,
        refresh_token=refresh_token
        )





@auth_router.post("/refresh-token")
async def refresh_token(data : RefreshTokenRequestSchema, db : AsyncSession = Depends(get_db), user : UserModel = Depends(get_user)):
    refresh_token_check_query = (
        select(RefreshTokenModel)
        .where(RefreshTokenModel.refresh_token == data.refresh_token and RefreshTokenModel.user_id == user.id)
    )

    refresh_token_result = await db.execute(refresh_token_check_query)

    refresh_token_exists = refresh_token_result.scalar_one_or_none()

    if refresh_token_exists is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid token"
        )

    new_access_token = create_access_token(user_id=user.id)

    return RefreshTokenResponseSchema(
        access_token=new_access_token,
        access_token_expiry=settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES * 60,
        refresh_token=refresh_token_exists.refresh_token
    )

    




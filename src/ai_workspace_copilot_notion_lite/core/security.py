from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from ai_workspace_copilot_notion_lite.core.db import get_db
from jose import JWTError
from sqlalchemy import select
from fastapi import status
from fastapi import HTTPException
from ai_workspace_copilot_notion_lite.models.auth_models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import secrets
import jwt
from datetime import timedelta
from datetime import timezone
from datetime import datetime
from ai_workspace_copilot_notion_lite.core.config import settings
from pwdlib import PasswordHash

from fastapi.security import OAuth2PasswordBearer


security = HTTPBearer()

password_hasher = PasswordHash.recommended()


def hash_password(password : str):
    return password_hasher.hash(password=password)




def verify_password(hashed_password : str, password : str):
    return password_hasher.verify(password=password, hash=hashed_password)




def create_access_token(user_id : str) -> str:
    payload = {
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_IN_MINUTES)
    }

    token = jwt.encode(
        algorithm=settings.ALGORITHM,
        key=settings.JWT_SECRET_KEY, 
        payload=payload
    )


    return token
    


def decode_jwt(token : str):
    decoded_token =  jwt.decode(
        token,
        key=settings.JWT_SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )

    return decoded_token



def create_refresh_token():
    return secrets.token_urlsafe(64)




async def get_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db : AsyncSession = Depends(get_db)
) -> UserModel:

    try:
        token = credentials.credentials
        payload = decode_jwt(
            token=token
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid token"
            )

    except (JWTError, ValueError):
        raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid or expired token"
            )
        
    query = (
        select(UserModel)
        .where(UserModel.id == user_id)
    )

    result = await db.execute(query)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Invalid or expired token"
    )

    return user
    
from uuid import UUID
from pydantic import EmailStr
from pydantic import Field
from pydantic import BaseModel, ConfigDict



class RegisterRequestSchema(BaseModel):
    name : str = Field(...)
    email : EmailStr = Field(...)
    password : str = Field(..., max_length=100)




class LoginRequestSchema(BaseModel):
    email : EmailStr
    password : str = Field(...)



class LoginResponseSchema(BaseModel):
    id : UUID
    name : str
    email : str
    access_token : str
    access_token_expiry : int
    refresh_token : str



class RefreshTokenRequestSchema(BaseModel):
    refresh_token : str


class RefreshTokenResponseSchema(BaseModel):
    refresh_token : str
    access_token : str
    access_token_expiry : int
    
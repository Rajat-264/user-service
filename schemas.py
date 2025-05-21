from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

class AddressBase(BaseModel):
    street: str
    city: str
    zip: str

    class Config:
        orm_mode = True

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str                             
    addresses: List[AddressBase]           

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class changePassword(BaseModel):
    password: str

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    addresses: List[AddressBase]  
    cart_items: List[CartItemBase]

    class Config:
        orm_mode = True

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"
    editor = "editor"

class UserWithRoles(User):
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponseWithToken(Token):
    user: User

class UpdateUserRequest(BaseModel):
    name: str
    phone: str
    addresses: List[AddressBase]
    cart: List[CartItemBase]

class Error(BaseModel):
    message: str

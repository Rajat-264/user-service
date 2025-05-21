from fastapi import FastAPI, Depends, HTTPException, status, Path, Body, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, get_db
import models, schemas, auth
from fastapi.middleware.cors import CORSMiddleware

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS setup
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# --------------------- AUTH HELPERS ---------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    username = auth.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --------------------- AUTH ROUTES ---------------------
@app.post("/users/signup", response_model=schemas.User)
def signup_user(user: schemas.SignupRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.name == user.name).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        phone=user.phone,
        role="customer"
    )

    for addr in user.addresses:
        new_user.addresses.append(models.Address(**addr.dict()))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/users/login", response_model=schemas.LoginResponseWithToken)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.post("/users/reset-password")
def reset_password(
    request: Request,
    resetpass: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == resetpass.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = auth.create_access_token(data={"sub": user.email})
    reset_link = f"{request.base_url}reset-password?token={access_token}"
    print("Reset link:", reset_link)
    return {"msg": "Password reset link has been generated"}

@app.get("/reset-password")
def verify_reset_password_form(token: str):
    email = auth.verify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"msg": "Token valid. Show reset password form"}

# --------------------- USER ROUTES ---------------------
@app.post("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/users/{userId}", response_model=schemas.User)
def update_user_info(
    userId: int = Path(...),
    updateInfo: schemas.UpdateUserRequest = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != userId and current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(models.User).filter(models.User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updateInfo.name
    user.phone = updateInfo.phone

    # Clear and update addresses
    user.addresses.clear()
    for addr in updateInfo.addresses:
        user.addresses.append(models.Address(**addr.dict()))

    # Clear and update cart items
    user.cart_items.clear()
    for cart_item in updateInfo.cart:
        user.cart_items.append(models.CartItem(product_id=cart_item.product_id, quantity=cart_item.quantity))

    db.commit()
    db.refresh(user)
    return user

@app.put("/users/{userId}/reset-password")
def change_password(
    userId: int = Path(...),
    newPassword: schemas.changePassword = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != userId and current_user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = db.query(models.User).filter(models.User.id == userId).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = auth.get_password_hash(newPassword.password)
    db.commit()
    return {"msg": "Password updated successfully"}

@app.get("/users/{userId}/role", response_model=schemas.UserRole)
def get_user_role(current_user: models.User = Depends(get_current_user)):
    return {"role": current_user.role}

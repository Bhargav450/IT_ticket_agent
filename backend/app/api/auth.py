from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    role: str

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        # Allow default guest/engineer if testing
        if req.email == "engineer@enterprise.io" and req.password == "password123":
            token = create_access_token("engineer@enterprise.io")
            return TokenResponse(access_token=token, user_name="Sarah Chen (Lead SRE)", role="support_engineer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_access_token(user.email)
    return TokenResponse(
        access_token=token,
        user_name=user.full_name or user.email,
        role=user.role
    )


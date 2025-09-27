# Simple FADO CRM Server with Authentication
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, create_tables
from models import NguoiDung, VaiTro
from auth import login_user, get_current_user
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="FADO CRM API",
    description="Simple CRM API with Authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "FADO CRM API is running", "status": "ok"}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Login endpoint
@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    try:
        result = login_user(db, login_data.email, login_data.password)
        return LoginResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Email hoac mat khau khong chinh xac")

# Get current user
@app.get("/auth/me")
async def get_me(current_user: NguoiDung = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "ho_ten": current_user.ho_ten,
        "vai_tro": current_user.vai_tro.value,
        "is_active": current_user.is_active
    }

# Simple dashboard stats
@app.get("/dashboard")
async def get_dashboard(current_user: NguoiDung = Depends(get_current_user)):
    """Get dashboard stats"""
    return {
        "message": f"Welcome {current_user.ho_ten}!",
        "role": current_user.vai_tro.value,
        "stats": {
            "customers": 0,
            "orders": 0,
            "revenue": 0
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
# app/auth/deps.py
import os, jwt
from fastapi import Header, HTTPException, status

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

def get_current_user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

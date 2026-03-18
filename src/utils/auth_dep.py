from fastapi import Request, HTTPException
from jose import jwt
from core.config import settings

def get_current_user(request: Request):

    SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET
    auth_token = request.cookies.get("access_token")

    if not auth_token:
        raise HTTPException(status_code=401, detail="Missing token")

    # token = auth_token.split(" ")[1]

    try:
        payload = jwt.decode(
            auth_token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            # audience="authenticated"
        )

        print('*' * 100)
        print(auth_token)
        print('*' *100)

        return payload

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
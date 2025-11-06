import os, json
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlmodel import Session, select
from .database import engine
from .models import User

JWT_SECRETS = json.loads(os.environ.get("JWT_SECRETS", '{"v1":"devsecret"}'))
JWT_CURRENT_KID = os.environ.get("JWT_CURRENT_KID", list(JWT_SECRETS.keys())[-1])
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60*24*7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def _get_current_time_utc():
    return datetime.now(datetime.timezone.utc)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = _get_current_time_utc + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    kid = JWT_CURRENT_KID
    secret = JWT_SECRETS.get(kid)  # ensure exists
    if not secret:
        raise RuntimeError("Invalid JWT_CURRENT_KID: no matching secret found")
    token = jwt.encode(to_encode, secret, algorithm=ALGORITHM, headers={"kid": kid})
    return token

def decode_token(token: str):
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')
        if not kid or kid not in JWT_SECRETS:
            raise JWTError('Invalid token key id')
        payload = jwt.decode(token, JWT_SECRETS[kid], algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise credentials_exception
        return user

# --- OAuth (SSO) Setup using Authlib ---
# Providers supported: google, github
OAUTH_REDIRECT_HOST = os.environ.get("OAUTH_REDIRECT_HOST", "http://localhost:8000")

oauth = OAuth()
# register providers using env variables if present
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"}
    )

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name="github",
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

# --- Apple ---
APPLE_CLIENT_ID = os.environ.get("APPLE_CLIENT_ID")
APPLE_TEAM_ID = os.environ.get("APPLE_TEAM_ID")
APPLE_KEY_ID = os.environ.get("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.environ.get("APPLE_PRIVATE_KEY")
if APPLE_CLIENT_ID and APPLE_TEAM_ID and APPLE_KEY_ID and APPLE_PRIVATE_KEY:
    oauth.register(
        name="apple",
        client_id=APPLE_CLIENT_ID,
        client_secret=None,  # Will be generated dynamically
        authorize_url="https://appleid.apple.com/auth/authorize",
        access_token_url="https://appleid.apple.com/auth/token",
        client_kwargs={"scope": "name email"},
    )

# --- Microsoft ---
MICROSOFT_CLIENT_ID = os.environ.get("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.environ.get("MICROSOFT_CLIENT_SECRET")
if MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET:
    oauth.register(
        name="microsoft",
        client_id=MICROSOFT_CLIENT_ID,
        client_secret=MICROSOFT_CLIENT_SECRET,
        access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
        authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        api_base_url="https://graph.microsoft.com/v1.0/",
        client_kwargs={"scope": "User.Read"},
    )

# --- Facebook ---
FACEBOOK_CLIENT_ID = os.environ.get("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.environ.get("FACEBOOK_CLIENT_SECRET")
if FACEBOOK_CLIENT_ID and FACEBOOK_CLIENT_SECRET:
    oauth.register(
        name="facebook",
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        access_token_url="https://graph.facebook.com/v13.0/oauth/access_token",
        authorize_url="https://www.facebook.com/v13.0/dialog/oauth",
        api_base_url="https://graph.facebook.com/v13.0/",
        client_kwargs={"scope": "email public_profile"},
    )

async def oauth_login_redirect(request: Request, provider: str):
    """
    Returns a Starlette Response that redirects the user to the provider's consent page.
    Called by router endpoint /api/oauth/{provider}
    """
    if provider not in oauth:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    redirect_uri = f"{OAUTH_REDIRECT_HOST}/api/oauth/{provider}/callback"
    return await oauth[provider].authorize_redirect(request, redirect_uri)

async def oauth_callback_and_issue_token(request: Request, provider: str):
    """
    Called on provider callback. Exchanges code for token, fetches user info,
    creates or finds a local user, and returns a JWT (as JSON).
    """
    if provider not in oauth:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    try:
        token = await oauth[provider].authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e.error} {e.description if hasattr(e,'description') else ''}")

    user_info = None

    if provider == "google":
        # OpenID Connect user info is in id_token or userinfo endpoint
        user_info = token.get("userinfo")
        # authlib often populates 'userinfo' when server_metadata_url is used; otherwise fetch
        if not user_info:
            user_info = await oauth.google.parse_id_token(request, token)
        # Ensure typical fields
        email = user_info.get("email")
        name = user_info.get("name") or user_info.get("given_name") or ""
        provider_uid = user_info.get("sub")

    elif provider == "github":
        # For GitHub, call user endpoint
        resp = await oauth.github.get("user", token=token)
        profile = resp.json()
        # email may not be public; fetch user/emails
        email = profile.get("email")
        if not email:
            # fetch list of emails
            emails_resp = await oauth.github.get("user/emails", token=token)
            for e in emails_resp.json() or []:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break
            if not email and (emails_resp.json() or []):
                email = emails_resp.json()[0].get("email")
        name = profile.get("name") or profile.get("login") or ""
        provider_uid = str(profile.get("id"))
    
    elif provider == "apple":
        # Apple returns id_token with user info (email)
        id_token = token.get("id_token")
        if id_token:
            payload = jwt.decode(id_token, options={"verify_signature": False})
            email = payload.get("email")
            name = payload.get("name", "")
            provider_uid = payload.get("sub")

    elif provider == "microsoft":
        resp = await oauth.microsoft.get("me", token=token)
        data = resp.json()
        email = data.get("userPrincipalName") or data.get("mail")
        name = data.get("displayName", "")
        provider_uid = data.get("id")

    elif provider == "facebook":
        resp = await oauth.facebook.get("me?fields=id,name,email", token=token)
        data = resp.json()
        email = data.get("email")
        name = data.get("name", "")
        provider_uid = data.get("id")
    
    else:
        raise HTTPException(status_code=400, detail="Provider not implemented")

    if not email:
        raise HTTPException(status_code=400, detail="Unable to obtain email from provider")

    # Create or get local user
    with Session(engine) as session:
        stmt = select(User).where(User.email == email)
        user = session.exec(stmt).first()
        if not user:
            # create local user with unusable password
            from .crud import create_user as crud_create_user
            # crud.create_user expects password; create a random unusable password but mark that user as SSO-created
            # Here we create directly to avoid double-hash issues and to keep created_at consistent
            user = crud_create_user(email, os.urandom(16).hex(), session)  # to ensure any additional logic in crud
            user.sso_created = True

    # Issue JWT with subject = user.id
    access_token = create_access_token({"sub": str(user.id)})
    # Return JSON with token. Frontend can redirect or store token.
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": name
        }
    }
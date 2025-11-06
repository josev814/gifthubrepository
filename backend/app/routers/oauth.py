import os
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from ..auth import oauth_login_redirect, oauth_callback_and_issue_token

router = APIRouter(prefix="/api/oauth", tags=["oauth"])

@router.get("/{provider}")
async def oauth_login(provider: str, request: Request):
    """
    Redirects the user to the provider's consent URL.
    Example: GET /api/oauth/google  -> redirect to Google consent
    """
    return await oauth_login_redirect(request, provider)

@router.get("/{provider}/callback")
async def oauth_callback(provider: str, request: Request):
    """
    Callback URL that provider redirects to.
    Returns a JSON with access_token. You can also redirect to front-end and append token as fragment.
    """
    token_response = await oauth_callback_and_issue_token(request, provider)
    # # For a nicer UX you may want to redirect to frontend and include the token in URL fragment for SPA to pick up.
    # # Example redirect:
    # frontend_url = os.getenv('FRONTEND_URL')  # adjust if needed or load from env
    # redirect_target = f"{frontend_url}/?access_token={token_response['access_token']}"
    # # Redirect user to frontend carrying the token in URL (fragment would be slightly safer; here we use query for simplicity)
    # return RedirectResponse(url=redirect_target)
    # Alternatively, you could `return JSONResponse(token_response)` if the frontend called this endpoint programmatically.
    return JSONResponse(token_response)

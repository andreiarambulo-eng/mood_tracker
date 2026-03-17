"""
Route-level authentication helpers.

Two authentication levels:
1. user_auth - Any authenticated user (own data only)
2. admin_auth - Admin role only
"""
from fastapi import Header, HTTPException, Depends, Request, Cookie
from typing import Optional, Annotated
from app.services.UserService import UserService
from app.models.UserModel import UserRole


async def get_authenticated_user(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    auth_token: Annotated[Optional[str], Cookie(name="auth_token")] = None
):
    """Authenticate any user via cookie or Bearer token."""
    token = None

    if auth_token:
        token = auth_token
    elif request.cookies.get("auth_token"):
        token = request.cookies.get("auth_token")
    elif authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Authentication required."}
        )

    user_service = UserService()
    user = user_service.verify_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Invalid or expired token"}
        )

    return user


async def get_admin_user(
    request: Request,
    authorization: Annotated[Optional[str], Header()] = None,
    auth_token: Annotated[Optional[str], Cookie(name="auth_token")] = None
):
    """Authenticate admin users only."""
    user = await get_authenticated_user(request, authorization, auth_token)

    if user.get('role') != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail={"success": False, "message": "Admin access required."}
        )

    return user


user_auth = Depends(get_authenticated_user)
admin_auth = Depends(get_admin_user)

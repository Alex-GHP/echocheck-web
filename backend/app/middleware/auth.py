from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.auth import UserResponse
from app.services.jwt import get_jwt_service
from app.services.users import get_user_service

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    """
    Dependency to get the current authenticated user

    Extracts and validates the JWT token from the Authorization header,
    then returns the corresponding user

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        UserResponse for the authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    jwt_service = get_jwt_service()
    user_service = get_user_service()

    token = credentials.credentials
    user_id = jwt_service.get_user_id_from_token(token, expected_type="access")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> UserResponse | None:
    """
    Dependency to optionally get the current authenticated user

    Same as get_current_user, but returns None instead of raising
    an exception if no valid token is provided.

    Useful for endpoints that behave differently for authenticated
    vs anonymous users

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        UserResponse if authenticated, None otherwise
    """
    if not credentials:
        return None

    jwt_service = get_jwt_service()
    user_service = get_user_service()

    token = credentials.credentials
    user_id = jwt_service.get_user_id_from_token(token, expected_type="access")

    if not user_id:
        return None

    return await user_service.get_user_by_id(user_id)

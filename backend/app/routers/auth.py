from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.middleware.auth import get_current_user
from app.models.auth import (
    AuthResponse,
    LoginInitRequest,
    LoginVerifyRequest,
    MessageResponse,
    RegisterInitRequest,
    RegisterVerifyRequest,
    ResendCodeRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserResponse,
    VerificationSentResponse,
    VerificationType,
)
from app.services.email import get_email_service
from app.services.jwt import get_jwt_service
from app.services.users import get_user_service
from app.services.verification import get_verification_service

router = APIRouter()


@router.post(
    "/register",
    response_model=VerificationSentResponse,
    status_code=status.HTTP_200_OK,
    summary="Step 1: Initiate registration",
)
async def register_init(request: RegisterInitRequest) -> VerificationSentResponse:
    """
    Start the registration process.

    - **email**: Valid email address (must be unique)
    - **password**: Password (8-128 characters)

    Creates a pending user account and sends a verification code to the email.
    The user must verify the code to complete registration.
    """
    user_service = get_user_service()
    verification_service = get_verification_service()
    settings = get_settings()

    existing_user = await user_service.get_user_by_email(request.email)
    if existing_user and existing_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    if existing_user and not existing_user.is_verified:
        await user_service.delete_unverified_user(request.email)

    try:
        await user_service.create_user(
            email=request.email, password=request.password, is_verified=False
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    success = await verification_service.create_and_send_code(
        email=request.email,
        verification_type=VerificationType.REGISTRATION,
    )

    if not success:
        await user_service.delete_unverified_user(request.email)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again.",
        )

    return VerificationSentResponse(
        message="Verification code sent to your email",
        email=request.email,
        expires_in_minutes=settings.verification_code_expire_minutes,
    )


@router.post(
    "/register/verify",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Step 2: Complete registration",
)
async def register_verify(request: RegisterVerifyRequest) -> AuthResponse:
    """
    Complete registration by verifying the code.

    - **email**: Email address used in registration
    - **code**: 6-digit verification code from email

    Returns user info and JWT tokens on success.
    """
    user_service = get_user_service()
    verification_service = get_verification_service()
    jwt_service = get_jwt_service()
    email_service = get_email_service()

    user = await user_service.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending registration found for this email",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified. Please login instead.",
        )

    is_valid = await verification_service.verify_code(
        email=request.email,
        code=request.code,
        verification_type=VerificationType.REGISTRATION,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    await user_service.verify_user(request.email)
    email_service.send_welcome_email(request.email)
    tokens = jwt_service.create_token_pair(user.id)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            is_verified=True,
            created_at=user.created_at,
        ),
        tokens=TokenResponse(**tokens),
    )


@router.post(
    "/login",
    response_model=VerificationSentResponse,
    summary="Step 1: Initiate login",
)
async def login_init(request: LoginInitRequest) -> VerificationSentResponse:
    """
    Start the login process.

    - **email**: User's email address
    - **password**: User's password

    Validates credentials and sends a verification code if valid.
    """
    user_service = get_user_service()
    verification_service = get_verification_service()
    settings = get_settings()

    user = await user_service.authenticate_user(
        email=request.email,
        password=request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please complete registration verification first",
        )

    success = await verification_service.create_and_send_code(
        email=request.email,
        verification_type=VerificationType.LOGIN,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again.",
        )

    return VerificationSentResponse(
        message="Verification code sent to your email",
        email=request.email,
        expires_in_minutes=settings.verification_code_expire_minutes,
    )


@router.post(
    "/login/verify",
    response_model=AuthResponse,
    summary="Step 2: Complete login",
)
async def login_verify(request: LoginVerifyRequest) -> AuthResponse:
    """
    Complete login by verifying the code.

    - **email**: Email address
    - **code**: 6-digit verification code from email

    Returns user info and JWT tokens on success.
    """
    user_service = get_user_service()
    verification_service = get_verification_service()
    jwt_service = get_jwt_service()

    user = await user_service.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_valid = await verification_service.verify_code(
        email=request.email,
        code=request.code,
        verification_type=VerificationType.LOGIN,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )

    tokens = jwt_service.create_token_pair(user.id)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
        tokens=TokenResponse(**tokens),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(request: TokenRefreshRequest) -> TokenResponse:
    """
    Get a new access token using a valid refresh token.

    - **refresh_token**: Valid refresh token

    Returns a new token pair.
    """
    jwt_service = get_jwt_service()
    user_service = get_user_service()

    user_id = jwt_service.get_user_id_from_token(
        request.refresh_token,
        expected_type="refresh",
    )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = jwt_service.create_token_pair(user_id)
    return TokenResponse(**tokens)


@router.post(
    "/resend-code",
    response_model=VerificationSentResponse,
    summary="Resend verification code",
)
async def resend_code(request: ResendCodeRequest) -> VerificationSentResponse:
    """
    Resend a verification code.

    - **email**: User's email address
    - **type**: Type of verification (registration or login)

    Use this if the previous code expired or wasn't received.
    """
    user_service = get_user_service()
    verification_service = get_verification_service()
    settings = get_settings()

    user = await user_service.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if request.type == VerificationType.REGISTRATION and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified",
        )

    if request.type == VerificationType.LOGIN and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please complete registration first",
        )

    success = await verification_service.create_and_send_code(
        email=request.email,
        verification_type=request.type,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again.",
        )

    return VerificationSentResponse(
        message="Verification code sent to your email",
        email=request.email,
        expires_in_minutes=settings.verification_code_expire_minutes,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """
    Get information about the currently authenticated user.

    Requires a valid access token in the Authorization header.
    """
    return current_user


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout current user",
)
async def logout(
    _current_user: UserResponse = Depends(get_current_user),
) -> MessageResponse:
    """
    Logout the current user.

    Requires a valid access token in the Authorization header.

    Note: Since JWTs are stateless, the client should discard the tokens
    after receiving this response. The tokens will remain valid until
    they expire, but the client should no longer use them.
    """
    return MessageResponse(message="Successfully logged out")

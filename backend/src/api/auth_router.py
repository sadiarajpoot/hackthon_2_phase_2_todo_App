from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any
from ..database import get_session
from ..schemas.user import UserCreate, UserResponse, UserLogin, Token
from ..services.auth_service import AuthService
from ..utils.security import verify_token
from ..utils.logging import get_logger
from ..utils.responses import APIResponse, raise_http_exception
from ..models.user import User

logger = get_logger(__name__)

auth_router = APIRouter()

# OAuth2 scheme for token authentication
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current user from token
    """
    try:
        payload = verify_token(token)
        if payload is None:
            raise_http_exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        email: str = payload.get("email")
        if email is None:
            raise_http_exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Get user from database
        db_gen = get_session()
        db = next(db_gen)
        try:
            user = await AuthService.get_user_by_email(email, db)
            if user is None:
                raise_http_exception(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return user
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error getting current user from token: {e}")
        raise_http_exception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@auth_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_session)) -> Any:
    """
    Register a new user
    """
    try:
        logger.info(f"Registration request for email: {user_data.email}")

        # Register the user
        user_response = await AuthService.register_user(user_data, db)

        logger.info(f"User registered successfully: {user_response.email}")
        return user_response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@auth_router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_session)) -> Any:
    """
    Login a user and return access token
    """
    try:
        logger.info(f"Login request for email: {user_credentials.email}")

        # Authenticate the user
        user = await AuthService.authenticate_user(
            user_credentials.email,
            user_credentials.password,
            db
        )

        if not user:
            logger.warning(f"Invalid credentials for email: {user_credentials.email}")
            raise_http_exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Create access token
        access_token = await AuthService.create_access_token_for_user(user)

        logger.info(f"User logged in successfully: {user.email}")

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@auth_router.post("/logout")
async def logout():
    """
    Logout a user (currently just a placeholder since we're using stateless JWT)
    """
    try:
        logger.info("Logout request received")
        # In a JWT-based system, logout is typically handled on the client side
        # by removing the token. This endpoint could be used for additional
        # server-side operations if needed in the future.

        return APIResponse.success(
            data=None,
            message="Successfully logged out"
        )

    except Exception as e:
        logger.error(f"Unexpected error during logout: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user info
    """
    try:
        logger.info(f"Getting current user info for: {current_user.email}")

        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            first_name=getattr(current_user, 'first_name', None),
            last_name=getattr(current_user, 'last_name', None),
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        )

    except Exception as e:
        logger.error(f"Unexpected error getting current user: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting user info"
        )
from sqlmodel import Session, select
from typing import Optional
from datetime import timedelta
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..utils.logging import get_logger
from ..utils.responses import raise_http_exception, not_found_exception
from fastapi import HTTPException, status

logger = get_logger(__name__)


class AuthService:
    @staticmethod
    async def register_user(user_data: UserCreate, db_session: Session) -> UserResponse:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = db_session.exec(
                select(User).where(User.email == user_data.email)
            ).first()

            if existing_user:
                raise_http_exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Create new user
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                first_name=getattr(user_data, 'first_name', None),  # Handle optional field
                last_name=getattr(user_data, 'last_name', None)     # Handle optional field
            )

            db_session.add(db_user)
            db_session.commit()
            db_session.refresh(db_user)

            logger.info(f"User registered successfully: {db_user.email}")

            return UserResponse(
                id=str(db_user.id),  # Convert UUID to string
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during registration"
            )

    @staticmethod
    async def authenticate_user(email: str, password: str, db_session: Session) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            # Find user by email
            user = db_session.exec(
                select(User).where(User.email == email)
            ).first()

            if not user or not verify_password(password, user.password_hash):
                logger.warning(f"Failed authentication attempt for email: {email}")
                return None

            if not user.is_active:
                logger.warning(f"Inactive user attempted login: {email}")
                return None

            logger.info(f"User authenticated successfully: {email}")
            return user

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    @staticmethod
    async def create_access_token_for_user(user: User) -> str:
        """Create access token for authenticated user"""
        try:
            data = {"sub": str(user.id), "email": user.email}
            token = create_access_token(
                data=data,
                expires_delta=timedelta(minutes=30)  # 30 minutes expiration
            )

            logger.info(f"Access token created for user: {user.email}")
            return token

        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating access token"
            )

    @staticmethod
    async def get_user_by_email(email: str, db_session: Session) -> Optional[User]:
        """Get user by email"""
        try:
            user = db_session.exec(
                select(User).where(User.email == email)
            ).first()

            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email: {e}")
            return None

    @staticmethod
    async def get_user_by_id(user_id: str, db_session: Session) -> Optional[User]:
        """Get user by ID"""
        try:
            user = db_session.exec(
                select(User).where(User.id == user_id)
            ).first()

            return user
        except Exception as e:
            logger.error(f"Error retrieving user by ID: {e}")
            return None
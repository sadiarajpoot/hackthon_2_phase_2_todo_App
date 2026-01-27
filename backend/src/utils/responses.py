from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class APIResponse:
    """Utility class for consistent API responses"""

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200):
        return {
            "success": True,
            "message": message,
            "data": data,
            "status_code": status_code
        }

    @staticmethod
    def error(message: str = "Error occurred", status_code: int = 400, details: Optional[Dict] = None):
        return {
            "success": False,
            "message": message,
            "data": None,
            "status_code": status_code,
            "details": details
        }


def create_error_response(message: str, status_code: int, details: Optional[Dict] = None):
    """Helper function to create error responses"""
    return APIResponse.error(message=message, status_code=status_code, details=details)


def raise_http_exception(
    status_code: int,
    detail: str,
    headers: Optional[Dict[str, str]] = None
):
    """Helper function to raise HTTP exceptions"""
    raise HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def unauthorized_exception(detail: str = "Could not validate credentials"):
    """Helper function to raise unauthorized exception"""
    return raise_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def forbidden_exception(detail: str = "Not enough permissions"):
    """Helper function to raise forbidden exception"""
    return raise_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def not_found_exception(detail: str = "Item not found"):
    """Helper function to raise not found exception"""
    return raise_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )
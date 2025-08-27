from datetime import datetime
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    code: str

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: str
    validation_errors: Optional[List[ErrorDetail]] = None

def create_error_response(
    detail: str, 
    error_code: str, 
    validation_errors: Optional[List[ErrorDetail]] = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "detail": detail,
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if validation_errors:
        response["validation_errors"] = [error.dict() for error in validation_errors]
    return response

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle all HTTP exceptions with structured error responses"""
    if exc.status_code == 404:
        error_code = "RESOURCE_NOT_FOUND"
        if "User" in exc.detail:
            error_code = "USER_NOT_FOUND"
        elif "Item" in exc.detail:
            error_code = "ITEM_NOT_FOUND"
    elif exc.status_code == 401:
        error_code = "AUTHENTICATION_FAILED"
        if "credentials" in exc.detail.lower():
            error_code = "INVALID_CREDENTIALS"
        elif "email or password" in exc.detail.lower():
            error_code = "LOGIN_FAILED"
    elif exc.status_code == 400:
        error_code = "BAD_REQUEST"
        if "No fields to update" in exc.detail:
            error_code = "EMPTY_UPDATE"
        elif "already registered" in exc.detail:
            error_code = "DUPLICATE_EMAIL"
    else:
        error_code = f"HTTP_{exc.status_code}"
            
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            detail=exc.detail,
            error_code=error_code
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle 422 Validation errors"""
    validation_errors = []
    
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:]) if len(error["loc"]) > 1 else None
        validation_errors.append(ErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"].upper()
        ))
    
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            detail="Validation failed",
            error_code="VALIDATION_ERROR",
            validation_errors=validation_errors
        )
    )

async def auth_exception_handler(request: Request, exc: HTTPException):
    """Handle 401 Authentication errors"""
    if exc.status_code == 401:
        error_code = "AUTHENTICATION_FAILED"
        if "credentials" in exc.detail.lower():
            error_code = "INVALID_CREDENTIALS"
        elif "email or password" in exc.detail.lower():
            error_code = "LOGIN_FAILED"
            
        return JSONResponse(
            status_code=401,
            content=create_error_response(
                detail=exc.detail,
                error_code=error_code
            )
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general 500 errors"""
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            detail="Internal server error",
            error_code="INTERNAL_ERROR"
        )
    )
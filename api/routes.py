# API routes module
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    User
)
from api.config import SECURITY_CONFIG
from models.request import ResearchRequest
from models.response import ResearchResponse, TokenResponse, StatusResponse, ErrorResponse
from core.researcher import Researcher
from core.storage import get_research_result, list_research_results, delete_research_result

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for authentication
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=SECURITY_CONFIG["access_token_expire_minutes"])
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )

    # Calculate expiration time
    expires_at = datetime.utcnow() + access_token_expires

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }


@router.post("/research", response_model=ResearchResponse)
async def conduct_research(
        request: ResearchRequest,
        current_user: User = Depends(get_current_active_user)
):
    """
    Conduct research based on the provided query, report type, and tone
    """
    try:
        # Conduct research
        result = await Researcher.conduct_research(
            query=request.query,
            report_type=request.report_type,
            tone=request.tone
        )

        return result
    except ValueError as e:
        logger.error(f"Value error in research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error conducting research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while conducting research"
        )


@router.get("/research/{report_id}", response_model=ResearchResponse)
async def get_research(
        report_id: str = Path(..., description="ID of the research report"),
        current_user: User = Depends(get_current_active_user)
):
    """
    Get a research report by ID
    """
    result = await get_research_result(report_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research report with ID {report_id} not found"
        )

    return result


@router.get("/research", response_model=List[ResearchResponse])
async def list_research(
        limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
        current_user: User = Depends(get_current_active_user)
):
    """
    List research reports with pagination
    """
    results = await list_research_results(limit, offset)
    return results


@router.delete("/research/{report_id}", response_model=StatusResponse)
async def delete_research(
        report_id: str = Path(..., description="ID of the research report to delete"),
        current_user: User = Depends(get_current_active_user)
):
    """
    Delete a research report by ID
    """
    deleted = await delete_research_result(report_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research report with ID {report_id} not found"
        )

    return {
        "status": "success",
        "message": f"Research report with ID {report_id} deleted successfully"
    }
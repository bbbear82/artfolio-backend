import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user_id
from app.models.base import get_db
from app.schemas.augment import (
    AugmentRequest,
    AugmentResponse,
    TranslateRequest,
    TranslateResponse,
)
from app.services.openai_service import call_augment, call_translate
from app.services.usage_service import check_and_increment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["augment"])


@router.post("/augment", response_model=AugmentResponse)
async def augment(
    request: AugmentRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    try:
        remaining = await check_and_increment(db, user_id, "augment")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))

    try:
        result = await call_augment(
            studio_text=request.studio_text,
            terms=request.terms,
            title=request.title,
            notes=request.notes,
            mode=request.mode,
        )
    except Exception as e:
        logger.error("OpenAI augment call failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )

    response = JSONResponse(
        content=AugmentResponse(
            description=result.get("description"),
            definitions=result.get("definitions"),
            portfolio_statement=result.get("portfolio_statement"),
        ).model_dump()
    )
    response.headers["X-Quota-Remaining"] = str(remaining)
    return response


@router.post("/translate", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    if not request.description and not request.portfolio_statement and not request.term_definitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nothing to translate -- provide at least one field",
        )

    try:
        remaining = await check_and_increment(db, user_id, "translate")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))

    try:
        result = await call_translate(
            description=request.description,
            portfolio_statement=request.portfolio_statement,
            term_definitions=request.term_definitions,
            target_language=request.target_language,
        )
    except Exception as e:
        logger.error("OpenAI translate call failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )

    response = JSONResponse(
        content=TranslateResponse(
            translated_description=result.get("description"),
            translated_portfolio_statement=result.get("portfolio_statement"),
            translated_definitions=result.get("definitions"),
        ).model_dump()
    )
    response.headers["X-Quota-Remaining"] = str(remaining)
    return response

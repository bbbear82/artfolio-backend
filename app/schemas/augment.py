from typing import Literal

from pydantic import BaseModel, Field


class AugmentRequest(BaseModel):
    studio_text: str = Field(..., max_length=10000)
    terms: list[str] = Field(default_factory=list, max_length=30)
    title: str | None = None
    notes: str | None = None
    mode: Literal["description", "definitions", "portfolio", "all"]


class AugmentResponse(BaseModel):
    description: str | None = None
    definitions: dict[str, str] | None = None
    portfolio_statement: str | None = None


class TranslateRequest(BaseModel):
    description: str | None = None
    portfolio_statement: str | None = None
    term_definitions: dict[str, str] = Field(default_factory=dict)
    target_language: str = Field(..., min_length=2, max_length=10)


class TranslateResponse(BaseModel):
    translated_description: str | None = None
    translated_portfolio_statement: str | None = None
    translated_definitions: dict[str, str] | None = None

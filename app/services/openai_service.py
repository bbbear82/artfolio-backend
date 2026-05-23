import json
import logging

import httpx

from app.config import settings
from app.prompts.description import SYSTEM_PROMPT as DESC_PROMPT
from app.prompts.definitions import SYSTEM_PROMPT as DEFS_PROMPT
from app.prompts.portfolio import SYSTEM_PROMPT as PORT_PROMPT
from app.prompts.translation import SYSTEM_PROMPT_TEMPLATE as TRANS_PROMPT

logger = logging.getLogger(__name__)

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

ALL_SYSTEM_PROMPT = """You are an art education specialist. Given the lesson/showcase context from an art studio, the artwork title, medium/notes, and a list of art terms, produce ALL of the following:

1. A polished artwork description (100-200 words) covering subject, techniques, and artistic context.
2. Clear, concise definitions (1-2 sentences each) for every provided art term.
3. A formal portfolio/admission artist statement (150-250 words) covering concept, techniques, creative process, and artistic growth.

Write in third person. Do not fabricate details not supported by the provided context.

Return JSON with keys: "description", "definitions" (object mapping term to definition), "portfolio_statement"."""


def _build_user_message(
    studio_text: str,
    terms: list[str],
    title: str | None,
    notes: str | None,
) -> str:
    parts = [f"Studio context:\n{studio_text}"]
    if title:
        parts.append(f"Artwork title: {title}")
    if notes:
        parts.append(f"Medium/notes: {notes}")
    if terms:
        parts.append(f"Art terms: {', '.join(terms)}")
    return "\n\n".join(parts)


async def call_augment(
    studio_text: str,
    terms: list[str],
    title: str | None,
    notes: str | None,
    mode: str,
) -> dict:
    if mode == "description":
        system = DESC_PROMPT
    elif mode == "definitions":
        system = DEFS_PROMPT
    elif mode == "portfolio":
        system = PORT_PROMPT
    else:
        system = ALL_SYSTEM_PROMPT

    user_msg = _build_user_message(studio_text, terms, title, notes)
    return await _chat_completion(system, user_msg)


async def call_translate(
    description: str | None,
    portfolio_statement: str | None,
    term_definitions: dict[str, str],
    target_language: str,
) -> dict:
    system = TRANS_PROMPT.format(language=target_language)

    content_parts = []
    if description:
        content_parts.append(f"Description:\n{description}")
    else:
        content_parts.append("Description: null")

    if portfolio_statement:
        content_parts.append(f"Portfolio statement:\n{portfolio_statement}")
    else:
        content_parts.append("Portfolio statement: null")

    if term_definitions:
        defs_text = "\n".join(f"- {term}: {defn}" for term, defn in term_definitions.items())
        content_parts.append(f"Term definitions:\n{defs_text}")
    else:
        content_parts.append("Term definitions: null")

    user_msg = "\n\n".join(content_parts)
    return await _chat_completion(system, user_msg)


async def _chat_completion(system_prompt: str, user_message: str) -> dict:
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.openai_model,
        "max_tokens": settings.openai_max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }

    async with httpx.AsyncClient(timeout=settings.openai_timeout) as client:
        for attempt in range(2):
            response = await client.post(OPENAI_URL, headers=headers, json=payload)

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == 0:
                    import asyncio
                    await asyncio.sleep(2)
                    continue
                response.raise_for_status()

            response.raise_for_status()
            break

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error("OpenAI returned non-JSON content: %s", content[:200])
        raise ValueError("OpenAI returned invalid JSON response")

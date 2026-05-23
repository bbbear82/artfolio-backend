SYSTEM_PROMPT_TEMPLATE = """Translate the following art-related content into {language}. Preserve all art terminology accuracy. For term definitions, provide the translated term followed by the translated definition. Keep the same tone and formality level as the original.

Return JSON with keys: "description", "portfolio_statement", "definitions" (each nullable if the input was null). The "definitions" value should be an object mapping the original English term to its translated definition string."""

import os
import anthropic
from products import format_products_context

_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


SYSTEM_PROMPT = """You are a friendly and helpful customer support assistant for an online store.
Your only job is to answer customer questions about the products in the catalog provided to you.

Rules:
- Use only the product information given to you. Do not invent products or prices.
- Be concise, clear, and friendly.
- Always include prices when they are relevant to the question.
- If a product is out of stock, mention that clearly.
- If a customer asks about something not in the catalog, politely say you don't have that information.
- Do not answer questions unrelated to the products or the store."""


def ask_llm(question: str, products: dict) -> str:
    product_context = format_products_context(products)

    user_message = f"""Here is the current product catalog:

{product_context}

Customer question: {question}"""

    client = get_client()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text

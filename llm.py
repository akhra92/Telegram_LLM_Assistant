import ollama
from products import format_products_context

SYSTEM_PROMPT = """You are a friendly and helpful customer support assistant for an online store.
Your only job is to answer customer questions about the products in the catalog provided to you.

Rules:
- Always reply in the same language the customer used. If they write in Uzbek, reply in Uzbek. If Russian, reply in Russian. If English, reply in English.
- Use only the product information given to you. Do not invent products or prices.
- Be concise, clear, and friendly.
- Always include prices when they are relevant to the question.
- If a product is out of stock, mention that clearly.
- If a customer asks about something not in the catalog, politely say you don't have that information.
- Do not answer questions unrelated to the products or the store."""

MODEL = "qwen2.5:7b"


def ask_llm(question: str, products: dict) -> str:
    product_context = format_products_context(products)

    user_message = f"""Here is the current product catalog:

{product_context}

Customer question: {question}"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return response.message.content

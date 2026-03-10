import json
import os
from datetime import datetime

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")


def load_products() -> dict:
    if not os.path.exists(PRODUCTS_FILE):
        return {"products": [], "last_updated": None}
    with open(PRODUCTS_FILE, "r") as f:
        return json.load(f)


def save_products(data: dict):
    data["last_updated"] = datetime.now().isoformat()
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def format_products_context(data: dict) -> str:
    products = data.get("products", [])
    if not products:
        return "No products available in the catalog."

    lines = []
    for p in products:
        stock = "In stock" if p.get("in_stock", True) else "Out of stock"
        price = f"${p['price']:.2f}" if "price" in p else "Price not listed"
        line = f"- {p['name']} | {price} | Category: {p.get('category', 'General')} | {stock}"
        if p.get("description"):
            line += f"\n  Description: {p['description']}"
        lines.append(line)

    last_updated = data.get("last_updated", "unknown")
    return "\n".join(lines) + f"\n\n(Catalog last updated: {last_updated})"

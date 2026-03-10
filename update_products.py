"""
CLI tool for managing the product catalog.

Usage:
    python update_products.py list
    python update_products.py add
    python update_products.py edit
    python update_products.py delete
"""

import sys
from products import load_products, save_products


def list_products():
    data = load_products()
    products = data.get("products", [])
    if not products:
        print("No products in the catalog.")
        return
    print(f"\n{'ID':<5} {'Name':<30} {'Price':>10}  {'Category':<20} {'Stock'}")
    print("-" * 75)
    for p in products:
        stock = "Yes" if p.get("in_stock", True) else "No"
        price = f"${p['price']:.2f}" if "price" in p else "N/A"
        print(f"{p['id']:<5} {p['name']:<30} {price:>10}  {p.get('category', ''):<20} {stock}")
    print(f"\nLast updated: {data.get('last_updated', 'Never')}\n")


def add_product():
    print("\n-- Add new product --")
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    price = float(input("Price ($): ").strip())
    category = input("Category: ").strip()
    description = input("Description: ").strip()
    in_stock = input("In stock? (y/n) [y]: ").strip().lower()
    in_stock = in_stock != "n"

    data = load_products()
    products = data.get("products", [])
    new_id = max((p["id"] for p in products), default=0) + 1

    products.append({
        "id": new_id,
        "name": name,
        "price": price,
        "category": category,
        "description": description,
        "in_stock": in_stock,
    })
    data["products"] = products
    save_products(data)
    print(f"Added '{name}' with ID {new_id}.")


def edit_product():
    list_products()
    try:
        product_id = int(input("Enter product ID to edit: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    data = load_products()
    products = data.get("products", [])
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        print(f"No product with ID {product_id}.")
        return

    print(f"\nEditing '{product['name']}' (press Enter to keep current value)")

    name = input(f"Name [{product['name']}]: ").strip()
    if name:
        product["name"] = name

    price_str = input(f"Price [${product.get('price', '')}]: ").strip()
    if price_str:
        product["price"] = float(price_str)

    category = input(f"Category [{product.get('category', '')}]: ").strip()
    if category:
        product["category"] = category

    description = input(f"Description [{product.get('description', '')}]: ").strip()
    if description:
        product["description"] = description

    current_stock = "y" if product.get("in_stock", True) else "n"
    in_stock_str = input(f"In stock? (y/n) [{current_stock}]: ").strip().lower()
    if in_stock_str in ("y", "n"):
        product["in_stock"] = in_stock_str == "y"

    save_products(data)
    print(f"Product '{product['name']}' updated.")


def delete_product():
    list_products()
    try:
        product_id = int(input("Enter product ID to delete: ").strip())
    except ValueError:
        print("Invalid ID.")
        return

    data = load_products()
    products = data.get("products", [])
    new_products = [p for p in products if p["id"] != product_id]

    if len(new_products) == len(products):
        print(f"No product with ID {product_id}.")
        return

    confirm = input(f"Delete product ID {product_id}? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    data["products"] = new_products
    save_products(data)
    print(f"Product ID {product_id} deleted.")


COMMANDS = {
    "list": list_products,
    "add": add_product,
    "edit": edit_product,
    "delete": delete_product,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python update_products.py [list|add|edit|delete]")
        sys.exit(1)
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()

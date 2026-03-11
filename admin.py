"""
Admin commands for managing the product catalog directly via Telegram.

Commands (admin only):
  /products          — list all products
  /add               — add a new product (guided flow)
  /edit              — edit an existing product (guided flow)
  /delete            — delete a product (with confirmation)
  /cancel            — cancel the current operation
"""

import os
import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from products import load_products, save_products

logger = logging.getLogger(__name__)

# Conversation states
(
    ADD_NAME, ADD_PRICE, ADD_CATEGORY, ADD_DESCRIPTION, ADD_STOCK,
    EDIT_ID, EDIT_NAME, EDIT_PRICE, EDIT_CATEGORY, EDIT_DESCRIPTION, EDIT_STOCK,
    DELETE_ID, DELETE_CONFIRM,
) = range(13)

SKIP = "-"  # user sends this to keep current value when editing


def _admin_id() -> int | None:
    val = os.getenv("ADMIN_USER_ID")
    return int(val) if val else None


def _is_admin(user_id: int) -> bool:
    admin_id = _admin_id()
    return admin_id is None or user_id == admin_id


def _format_catalog(data: dict) -> str:
    products = data.get("products", [])
    if not products:
        return "The catalog is empty."
    lines = [f"*Product Catalog* ({len(products)} items)\n"]
    for p in products:
        stock = "✅ In stock" if p.get("in_stock", True) else "❌ Out of stock"
        price = f"${p['price']:.2f}" if "price" in p else "N/A"
        lines.append(
            f"*ID {p['id']}* — {p['name']}\n"
            f"  Price: {price} | Category: {p.get('category', '—')} | {stock}\n"
            f"  {p.get('description', '')}"
        )
    return "\n".join(lines)


# ── /products ────────────────────────────────────────────────────────────────

async def cmd_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return
    data = load_products()
    await update.message.reply_text(_format_catalog(data), parse_mode="Markdown")


# ── /add ─────────────────────────────────────────────────────────────────────

async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END
    context.user_data.clear()
    await update.message.reply_text("*Adding a new product.*\n\nProduct name?", parse_mode="Markdown")
    return ADD_NAME


async def add_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Price in USD (e.g. `9.99`):", parse_mode="Markdown")
    return ADD_PRICE


async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["price"] = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Please enter a valid number (e.g. `9.99`):", parse_mode="Markdown")
        return ADD_PRICE
    await update.message.reply_text("Category (e.g. Electronics, Accessories):")
    return ADD_CATEGORY


async def add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["category"] = update.message.text.strip()
    await update.message.reply_text("Short description:")
    return ADD_DESCRIPTION


async def add_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text.strip()
    await update.message.reply_text("Is it in stock? (yes / no):")
    return ADD_STOCK


async def add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip().lower()
    if answer not in ("yes", "no", "y", "n"):
        await update.message.reply_text("Please reply *yes* or *no*:", parse_mode="Markdown")
        return ADD_STOCK

    data = load_products()
    products = data.get("products", [])
    new_id = max((p["id"] for p in products), default=0) + 1
    new_product = {
        "id": new_id,
        "name": context.user_data["name"],
        "price": context.user_data["price"],
        "category": context.user_data["category"],
        "description": context.user_data["description"],
        "in_stock": answer in ("yes", "y"),
    }
    products.append(new_product)
    data["products"] = products
    save_products(data)

    await update.message.reply_text(
        f"✅ *{new_product['name']}* added with ID {new_id}.", parse_mode="Markdown"
    )
    logger.info("Admin added product: %s", new_product)
    return ConversationHandler.END


# ── /edit ─────────────────────────────────────────────────────────────────────

async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END
    data = load_products()
    await update.message.reply_text(
        _format_catalog(data) + "\n\nEnter the *ID* of the product to edit:",
        parse_mode="Markdown",
    )
    return EDIT_ID


async def edit_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Please enter a valid numeric ID:")
        return EDIT_ID

    data = load_products()
    product = next((p for p in data.get("products", []) if p["id"] == product_id), None)
    if not product:
        await update.message.reply_text(f"No product with ID {product_id}. Try again:")
        return EDIT_ID

    context.user_data["edit_id"] = product_id
    context.user_data["product"] = product
    await update.message.reply_text(
        f"Editing *{product['name']}*.\nSend `-` to keep the current value.\n\n"
        f"Name [{product['name']}]:",
        parse_mode="Markdown",
    )
    return EDIT_NAME


async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val != SKIP:
        context.user_data["product"]["name"] = val
    p = context.user_data["product"]
    await update.message.reply_text(f"Price [${p.get('price', '')}]:")
    return EDIT_PRICE


async def edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val != SKIP:
        try:
            context.user_data["product"]["price"] = float(val)
        except ValueError:
            await update.message.reply_text("Invalid price. Enter a number or `-` to skip:")
            return EDIT_PRICE
    p = context.user_data["product"]
    await update.message.reply_text(f"Category [{p.get('category', '')}]:")
    return EDIT_CATEGORY


async def edit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val != SKIP:
        context.user_data["product"]["category"] = val
    p = context.user_data["product"]
    await update.message.reply_text(f"Description [{p.get('description', '')}]:")
    return EDIT_DESCRIPTION


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip()
    if val != SKIP:
        context.user_data["product"]["description"] = val
    p = context.user_data["product"]
    current = "yes" if p.get("in_stock", True) else "no"
    await update.message.reply_text(f"In stock? (yes / no / `-` to keep) [{current}]:")
    return EDIT_STOCK


async def edit_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    val = update.message.text.strip().lower()
    if val != SKIP:
        if val not in ("yes", "no", "y", "n"):
            await update.message.reply_text("Please reply *yes*, *no*, or `-` to skip:", parse_mode="Markdown")
            return EDIT_STOCK
        context.user_data["product"]["in_stock"] = val in ("yes", "y")

    data = load_products()
    products = data.get("products", [])
    for i, p in enumerate(products):
        if p["id"] == context.user_data["edit_id"]:
            products[i] = context.user_data["product"]
            break
    data["products"] = products
    save_products(data)

    name = context.user_data["product"]["name"]
    await update.message.reply_text(f"✅ *{name}* updated.", parse_mode="Markdown")
    logger.info("Admin updated product ID %s", context.user_data["edit_id"])
    return ConversationHandler.END


# ── /delete ──────────────────────────────────────────────────────────────────

async def delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return ConversationHandler.END
    data = load_products()
    await update.message.reply_text(
        _format_catalog(data) + "\n\nEnter the *ID* of the product to delete:",
        parse_mode="Markdown",
    )
    return DELETE_ID


async def delete_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        product_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Please enter a valid numeric ID:")
        return DELETE_ID

    data = load_products()
    product = next((p for p in data.get("products", []) if p["id"] == product_id), None)
    if not product:
        await update.message.reply_text(f"No product with ID {product_id}. Try again:")
        return DELETE_ID

    context.user_data["delete_id"] = product_id
    context.user_data["delete_name"] = product["name"]
    await update.message.reply_text(
        f"Delete *{product['name']}*? Reply *yes* to confirm or *no* to cancel.",
        parse_mode="Markdown",
    )
    return DELETE_CONFIRM


async def delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip().lower()
    if answer not in ("yes", "no", "y", "n"):
        await update.message.reply_text("Please reply *yes* or *no*:", parse_mode="Markdown")
        return DELETE_CONFIRM

    if answer in ("no", "n"):
        await update.message.reply_text("Cancelled.")
        return ConversationHandler.END

    data = load_products()
    product_id = context.user_data["delete_id"]
    data["products"] = [p for p in data.get("products", []) if p["id"] != product_id]
    save_products(data)

    name = context.user_data["delete_name"]
    await update.message.reply_text(f"🗑️ *{name}* deleted.", parse_mode="Markdown")
    logger.info("Admin deleted product ID %s", product_id)
    return ConversationHandler.END


# ── /cancel ──────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


# ── Handler builders ─────────────────────────────────────────────────────────

def build_admin_handlers():
    text = filters.TEXT & ~filters.COMMAND

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            ADD_NAME:        [MessageHandler(text, add_name)],
            ADD_PRICE:       [MessageHandler(text, add_price)],
            ADD_CATEGORY:    [MessageHandler(text, add_category)],
            ADD_DESCRIPTION: [MessageHandler(text, add_description)],
            ADD_STOCK:       [MessageHandler(text, add_stock)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    edit_conv = ConversationHandler(
        entry_points=[CommandHandler("edit", edit_start)],
        states={
            EDIT_ID:          [MessageHandler(text, edit_id)],
            EDIT_NAME:        [MessageHandler(text, edit_name)],
            EDIT_PRICE:       [MessageHandler(text, edit_price)],
            EDIT_CATEGORY:    [MessageHandler(text, edit_category)],
            EDIT_DESCRIPTION: [MessageHandler(text, edit_description)],
            EDIT_STOCK:       [MessageHandler(text, edit_stock)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    delete_conv = ConversationHandler(
        entry_points=[CommandHandler("delete", delete_start)],
        states={
            DELETE_ID:      [MessageHandler(text, delete_id)],
            DELETE_CONFIRM: [MessageHandler(text, delete_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    return [
        CommandHandler("products", cmd_products),
        add_conv,
        edit_conv,
        delete_conv,
    ]

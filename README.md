# Telegram Product Assistant Bot

A Telegram bot that answers customer questions about your product catalog using Qwen AI running locally. Works in private chats and group chats. Store owners can manage the product catalog directly from Telegram — no terminal required.

## Features

- Answers customer questions about products: prices, availability, descriptions, categories
- Powered by Qwen 3 (8B) running locally via Ollama — no API key required
- Works in private chats and group chats (mention the bot to trigger it in groups)
- Admin commands to add, edit, and delete products directly from Telegram
- Shows a typing indicator while generating a response

## Project Structure

```
.
├── main.py              # Bot entry point — registers all handlers
├── llm.py               # Qwen/Ollama integration and system prompt
├── admin.py             # Admin Telegram commands for catalog management
├── products.py          # Product catalog loader and formatter
├── update_products.py   # (Optional) CLI tool for catalog management
├── products.json        # Product catalog data
├── .env.example         # Environment variable template
└── requirements.txt     # Python dependencies
```

## Implementation Steps

### 1. Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts to choose a name and username
3. Copy the **bot token** — you will need it in step 5

### 2. Get your Telegram user ID (for admin access)

1. Search for **@userinfobot** on Telegram
2. Send `/start` — it will reply with your user ID (a number like `123456789`)
3. Save it — you will need it in step 5

### 3. Install Ollama and pull the model

Install **Ollama** from [ollama.com](https://ollama.com), then pull the Qwen model:

```bash
ollama pull qwen3:8b
```

> Qwen 3 8B is ~5.2 GB. For a lighter option use `qwen3:4b`; for better quality use `qwen3:14b`. Change the model name in `llm.py` if needed.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
ADMIN_USER_ID=your_telegram_user_id_here
```

- **TELEGRAM_TOKEN** — from BotFather (step 1)
- **ADMIN_USER_ID** — your numeric Telegram user ID (step 2). Only this user can use admin commands. If left unset, all users can manage products.

### 6. Run the bot

Make sure Ollama is running, then start the bot:

```bash
ollama serve   # if not already running as a service
python main.py
```

The bot will start polling for messages. Press `Ctrl+C` to stop.

---

## Managing the Product Catalog

Products can be managed directly inside Telegram using admin commands — no terminal or file editing needed.

### Admin commands

| Command      | Description                          |
|--------------|--------------------------------------|
| `/products`  | List all products in the catalog     |
| `/add`       | Add a new product (guided flow)      |
| `/edit`      | Edit an existing product (guided)    |
| `/delete`    | Delete a product (with confirmation) |
| `/cancel`    | Cancel the current operation         |

### How it works

Each command starts a guided conversation. The bot asks one question at a time:

**Adding a product (`/add`)**
```
You:  /add
Bot:  Adding a new product. Product name?
You:  Wireless Mouse
Bot:  Price in USD?
You:  24.99
Bot:  Category?
You:  Electronics
Bot:  Short description?
You:  Ergonomic wireless mouse, 2.4GHz, 12-month battery
Bot:  Is it in stock? (yes / no)
You:  yes
Bot:  ✅ Wireless Mouse added with ID 6.
```

**Editing a product (`/edit`)**

The bot shows the catalog and asks for a product ID. For each field, send a new value or `-` to keep the current one.

**Deleting a product (`/delete`)**

The bot shows the catalog, asks for an ID, then asks for confirmation before deleting.

### Product fields

| Field         | Type    | Description                        |
|---------------|---------|------------------------------------|
| `id`          | int     | Auto-incremented unique identifier |
| `name`        | string  | Product name                       |
| `price`       | float   | Price in USD                       |
| `category`    | string  | Product category                   |
| `description` | string  | Short product description          |
| `in_stock`    | boolean | Availability status                |

---

## Customer Usage

### Private chat

Send any message to the bot and it will answer based on the product catalog.

### Group chat

Add the bot to a group and mention it in your message:

```
@YourBotName do you have wireless headphones?
```

The bot only responds when explicitly mentioned in groups.

---

## Dependencies

| Package               | Purpose                              |
|-----------------------|--------------------------------------|
| `python-telegram-bot` | Telegram Bot API client              |
| `ollama`              | Ollama client for local LLM inference|
| `python-dotenv`       | Load environment variables from .env |

# Telegram Product Assistant Bot

A Telegram bot that answers customer questions about your product catalog using Claude AI. Works in both private chats and group chats (responds only when mentioned in groups).

## Features

- Answers customer questions about products: prices, availability, descriptions, categories
- Powered by Qwen 2.5 (7B) running locally via Ollama — no API key required
- Works in private chats and group chats (mention the bot to trigger it)
- Shows a typing indicator while generating a response
- CLI tool to manage the product catalog (add, edit, delete, list)

## Project Structure

```
.
├── main.py              # Telegram bot entry point
├── llm.py               # Claude API integration and system prompt
├── products.py          # Product catalog loader and formatter
├── update_products.py   # CLI tool for managing products
├── products.json        # Product catalog data
├── .env.example         # Environment variable template
└── requirements.txt     # Python dependencies
```

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd Telegram_Assistant
```

### 2. Install Ollama and pull the model

Install [Ollama](https://ollama.com) then pull the Qwen model:

```bash
ollama pull qwen2.5:7b
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in your Telegram token:

```bash
cp .env.example .env
```

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
```

- **TELEGRAM_TOKEN**: Get one from [@BotFather](https://t.me/BotFather) on Telegram.

> No API key needed — the model runs locally via Ollama.

### 5. Run the bot

```bash
python main.py
```

## Managing the Product Catalog

Use the CLI tool to manage products without editing JSON manually:

```bash
# List all products
python update_products.py list

# Add a new product
python update_products.py add

# Edit an existing product
python update_products.py edit

# Delete a product
python update_products.py delete
```

Product data is stored in `products.json` with the following fields per product:

| Field         | Type    | Description                        |
|---------------|---------|------------------------------------|
| `id`          | int     | Auto-incremented unique identifier |
| `name`        | string  | Product name                       |
| `price`       | float   | Price in USD                       |
| `category`    | string  | Product category                   |
| `description` | string  | Short product description          |
| `in_stock`    | boolean | Availability status                |

## Usage

### Private chat

Send any message to the bot directly and it will answer based on the product catalog.

### Group chat

Add the bot to a group and mention it in your message:

```
@YourBotName do you have wireless headphones?
```

The bot will only respond when explicitly mentioned in groups.

## Dependencies

| Package               | Purpose                        |
|-----------------------|--------------------------------|
| `python-telegram-bot` | Telegram Bot API client        |
| `ollama`              | Ollama client for local LLMs   |
| `python-dotenv`       | Load environment variables     |

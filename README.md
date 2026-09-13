# channels

Telegram botini Claude (Anthropic API) bilan bog'laydigan oddiy xizmat. Foydalanuvchi
Telegramda yozgan xabari Claude'ga yuboriladi va javobi qaytariladi; har bir chat uchun
suhbat tarixi saqlanadi.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Sozlash

1. [@BotFather](https://t.me/BotFather) orqali yangi Telegram bot yarating va tokenini oling.
2. [Anthropic Console](https://console.anthropic.com/)dan API kalitini oling.
3. `.env.example` faylini `.env` deb nusxalab, qiymatlarni to'ldiring:

```bash
cp .env.example .env
```

```
TELEGRAM_BOT_TOKEN=...
ANTHROPIC_API_KEY=...
CLAUDE_MODEL=claude-sonnet-5
```

## Ishga tushirish

```bash
python bot.py
```

Botga Telegramda `/start` yuboring va suhbatni boshlang. Suhbat tarixini tozalash uchun
`/reset` buyrug'idan foydalaning.

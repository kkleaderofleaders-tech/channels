# channels

Telegram botini Groq API (bepul, ochiq modellar) bilan bog'laydigan oddiy xizmat.
Foydalanuvchi Telegramda yozgan xabari AI modelga yuboriladi va javobi qaytariladi;
har bir chat uchun suhbat tarixi saqlanadi.

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Sozlash

1. [@BotFather](https://t.me/BotFather) orqali yangi Telegram bot yarating va tokenini oling.
2. [Groq Console](https://console.groq.com/keys)dan bepul API kalitini oling (karta talab qilinmaydi).
3. `.env.example` faylini `.env` deb nusxalab, qiymatlarni to'ldiring:

```bash
cp .env.example .env
```

```
TELEGRAM_BOT_TOKEN=...
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile
```

## Ishga tushirish

```bash
python bot.py
```

Botga Telegramda `/start` yuboring va suhbatni boshlang. Suhbat tarixini tozalash uchun
`/reset` buyrug'idan foydalaning.

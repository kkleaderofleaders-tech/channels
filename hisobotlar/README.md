# Oylik hisobotlar — Natija maktabi

Ota-onalar uchun oylik hisobot PDF'larini yaratish tizimi. Maʼlumotni `oylik-hisobot` sub-agenti (`.claude/agents/oylik-hisobot.md`) Durbin va boshqa manbalardan yigʻadi, tahlil qiladi va shu papkadagi shablon orqali PDF qiladi.

## Ishlatish

Claude Code'da:

```
oylik-hisobot agenti bilan 5-A sinfi uchun sentabr oyi hisobotlarini tayyorla
```

yoki bitta oʻquvchi uchun: `... Aliyev Sardor uchun sentabr hisobotini PDF qilib ber`.

Qoʻlda (tayyor JSON boʻlsa):

```bash
node hisobotlar/render.cjs hisobotlar/namuna/namuna.json            # → namuna.pdf
node hisobotlar/render.cjs kirish.json chiqish.pdf --html           # HTML ni ham saqlaydi
```

Talab: Node.js va Playwright (Chromium). Bulut sessiyasida oldindan oʻrnatilgan; lokal kompyuterda: `npm i -g playwright && npx playwright install chromium`.

## Papkalar

| Yoʻl | Nima |
| --- | --- |
| `render.cjs` | JSON → HTML → PDF |
| `shablon/hisobot.css` | A4 sahifa uslubi — "Natija maktabi" dizayn tizimi tokenlari |
| `brand/` | Brendbukdagi asl logotip va grafik element SVG'lari, Geist shrifti (OFL) |
| `namuna/` | Namuna JSON va PDF (soxta maʼlumot) |
| `manbalar/` | Qoʻshimcha manbalar (olimpiada natijalari, toʻgarak qaydnomasi va h.k.) — gitga tushmaydi |
| `chiqish/<YYYY-MM>/<sinf>/` | Tayyor hisobotlar — **gitga tushmaydi** (shaxsiy maʼlumot) |

## JSON formati

Majburiy faqat `davr` va `oquvchi`; qolgan boʻlimlar boʻlmasa, PDF'da chiqmaydi.

```jsonc
{
  "davr": { "oy": "Sentabr", "yil": 2026, "boshlanish": "2026-09-01", "tugash": "2026-09-30" },
  "oquvchi": { "ism": "Familiya Ism", "sinf": "5-A", "sinf_rahbari": "…", "tutor": "…" },
  "ota_ona": { "ism": "…" },                       // "Hurmatli … !" qatori
  "korsatkichlar": [                                // ≤ 4 ta statistika pufakchasi
    { "nom": "Oʻrtacha baho", "qiymat": "4.62", "izoh": "avgustdagi 4.48 dan yuqori" }
  ],
  "umumiy_xulosa": "3–5 gap",
  "fanlar": [
    { "fan": "Matematika", "ortacha": 4.64, "oldingi_oy": 4.8, "sinf_ortacha": 4.35,
      "baholar_soni": 14, "izoh": "ixtiyoriy qisqa izoh" }
  ],
  "davomat": { "otilgan_darslar": 121, "qoldirilgan": 4, "kechikkan": 0, "kasal": 0, "izoh": "…" },
  "haftalik_ballar": [ { "nom": "Uy vazifasi", "qiymat": "7.8 / 10" } ],
  "progress_imtihonlar": [ { "fan": "Matematika", "sana": "2026-09-25", "turi": "Test", "natija": 4, "maksimal": 5 } ],
  "kuchli_tomonlar": [ { "sarlavha": "…", "tafsilot": "raqam bilan" } ],
  "kamchiliklar":    [ { "sarlavha": "…", "tafsilot": "raqam bilan" } ],
  "tavsiyalar": [ { "kimga": "Ota-onaga | Oʻquvchiga | Maktab tomonidan", "matn": "…" } ],
  "keyingi_oy_maqsadlari": [ "…" ],
  "qoshimcha": [ { "sarlavha": "Olimpiada", "matn": "…" } ],
  "imzo": { "sinf_rahbari": "…", "direktor_orinbosari": "…", "sana": "2026-10-03" },
  "manbalar": [ "Durbin: baholar, 2026-09-01 — 2026-09-30" ],
  "namuna": false                                   // true → muqovada "Namuna" belgisi
}
```

## Brend qoidalari (shablonda allaqachon bor)

- Toʻrtta rang: Honor Roll `#dd1717`, Blank Page `#ffffff`, Blackout Exam `#070707`, Recess Bell `#ff4a4a` (faqat grafik shakl uchun, matn emas).
- Qizil yuzada faqat oq matn. Soya va gradient yoʻq.
- Shrift — Geist (Bold sarlavha, Medium subtitr, Regular matn).
- Logotip faqat burchakda: muqovada oq gorizontal logotip yuqori chapda, oxirida bir qatorli logotip quyi chapda.
- Oʻzbek apostrofi: `oʻ`, `gʻ` (U+02BB). `render.cjs` oddiy `'` ni avtomatik almashtiradi.

Manba: claude.ai'dagi "Natija maktabi" dizayn tizimi (Anqo jamoasi brendbuki asosida).

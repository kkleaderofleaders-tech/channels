#!/usr/bin/env python3
"""NATIJA maktabi — SMS shablonlari reyestri (TT-IT-SMS-01) PDF generatori."""
import re, html, os, sys
import pymupdf
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.join(HERE, 'brand')
FONTS = os.path.join(HERE, 'fonts')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out.pdf')

DOC_DATE = '23.09.2026'
SCHOOL = 'NATIJA maktabi'
SIG = 'NATIJA maktabi.'

TEL_MAIN = '+998 70 225 90 90'
TEL_BUX = '+998 77 260 99 96'
TEL_DIR = '+998 99 576 77 76'
TG = '@natija_maktabi'
DIRECTOR = 'Artikov Islombek'

# ---------------------------------------------------------------- helpers
GSM_BASIC = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
                "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
GSM_EXT = set("^{}\\[~]|€\f")


def gsm_len(s):
    n = 0
    for c in s:
        if c in GSM_BASIC:
            n += 1
        elif c in GSM_EXT:
            n += 2
        else:
            raise ValueError(f'GSM-7 dan tashqari belgi {c!r} matnda: {s}')
    return n


def prose(s):
    """Brend qoidasi: o'zbek apostrofi hujjat matnida teskari (U+02BB), tutuq belgisi U+02BC."""
    s = re.sub(r"([OoGg])'", '\\1\u02bb', s)
    s = re.sub(r"(?<=[A-Za-z])'(?=[A-Za-z])", '\u02bc', s)
    return s


def esc(s):
    return html.escape(s, quote=False)


def P(s):
    return esc(prose(s))


# ---------------------------------------------------------------- data
SAMPLE = {
    'ism': 'Diyorbek Rahimov', 'sinf': '5-A', 'oy': 'Mart', 'yil': '2026-2027',
    'sana': '10-mart', 'sana2': '14-mart', 'sana3': '16-mart', 'vaqt': '09:00',
    'summa': '3 500 000', 'foiz': '15', 'son': '3', 'daqiqa': '20', 'ball': '86',
    'tel': TEL_MAIN, 'tel2': TEL_BUX, 'kod': '4821', 'raqam': '1057', 'muddat': '24 soat',
    'fan': 'Matematika', 'chorak': '3-chorak', 'bayram': "Navro'z bayrami",
    'tanlov': 'BOND olimpiadasi', 'imtihon': 'IELTS', 'orin': "1-o'rin", 'natija': '7.0',
    'yutuq': 'faolligi va odobi', 'mavzu': 'Bolada diqqat sustligi',
    'manzil': 'Xiva sh., NATIJA maktabi', 'hujjat': "tug'ilganlik guvohnomasi",
    'havola': 't.me/natija_maktabi', 'kanal': TG,
}

VARIABLES = [
    ('{ism}', "O'quvchi ism-familiyasi", 30, 'Diyorbek Rahimov'),
    ('{sinf}', 'Sinf nomi', 5, '5-A'),
    ('{oy}', 'Oy nomi', 10, 'Mart'),
    ('{yil}', "O'quv yili", 10, '2026-2027'),
    ('{sana}, {sana2}, {sana3}', 'Sana (10-mart)', 12, '10-mart'),
    ('{vaqt}', 'Soat (09:00)', 5, '09:00'),
    ('{summa}', "Summa, so'mda", 12, '3 500 000'),
    ('{foiz}', 'Chegirma foizi', 3, '15'),
    ('{son}, {daqiqa}, {ball}', 'Raqamli qiymat', 4, '3'),
    ('{tel}, {tel2}', 'Telefon raqam (3-bo\'limdagi aloqa raqamlaridan biri)', 18, TEL_MAIN),
    ('{kod}', 'Bir martalik kod (OTP)', 6, '4821'),
    ('{raqam}', 'Murojaat raqami', 8, '1057'),
    ('{muddat}', 'Muddat (24 soat)', 12, '24 soat'),
    ('{fan}', 'Fan nomi', 20, 'Matematika'),
    ('{chorak}', 'Chorak nomi', 12, '3-chorak'),
    ('{bayram}', 'Bayram nomi', 25, "Navro'z bayrami"),
    ('{tanlov}, {imtihon}', 'Tanlov/imtihon nomi', 25, 'BOND olimpiadasi'),
    ('{orin}, {natija}', 'Natija qiymati', 12, "1-o'rin"),
    ('{yutuq}', "Yutuq ta'rifi", 25, 'faolligi va odobi'),
    ('{mavzu}', 'Seminar mavzusi', 30, 'Bolada diqqat sustligi'),
    ('{manzil}', 'Manzil', 30, 'Xiva sh., NATIJA maktabi'),
    ('{hujjat}', 'Hujjat nomi', 30, "tug'ilganlik guvohnomasi"),
    ('{havola}, {kanal}', 'Havola / Telegram kanal', 25, TG),
]

B = TEL_BUX
D = TEL_DIR

BLOCKS = [
 ('A', "TO'LOV VA MOLIYA", 'Ota-ona', [
  ('A-01', "Oy boshi to'lov eslatmasi", "Hurmatli ota-ona! {oy} oyi to'lovi {sana} gacha to'lanishi so'raladi. Summa: {summa} so'm. Aloqa: {tel}. %S", {'tel': B}),
  ('A-02', "To'lov muddati bugun tugaydi", "Hurmatli ota-ona! {ism} uchun to'lov muddati bugun tugaydi. Summa: {summa} so'm. Iltimos, bugun to'lang. %S", {}),
  ('A-03', "Kechikkan to'lov (takroriy)", "Hurmatli ota-ona! {ism} bo'yicha {summa} so'm qarzdorlik mavjud. Buxgalteriya: {tel}. %S", {'tel': B}),
  ('A-04', "To'lov qabul qilindi (tasdiq)", "Hurmatli ota-ona! {summa} so'm to'lovingiz qabul qilindi. Rahmat! Balans Durbin tizimida. %S", {}),
  ('A-05', "Chegirma qo'llandi", "Hurmatli ota-ona! {ism} uchun {foiz}% chegirma qo'llandi. Yangi summa: {summa} so'm. %S", {}),
  ('A-06', "Ortiqcha to'lov qaytarildi", "Hurmatli ota-ona! Ortiqcha to'lov {summa} so'm qaytarildi. Savollar: {tel}. %S", {'tel': B}),
  ('A-07', "Yangi o'quv yili shartnomasi", "Hurmatli ota-ona! {yil} o'quv yili shartnomasi tayyor. Imzolash uchun murojaat qiling: {tel}. %S", {}),
  ('A-08', 'Shartnoma imzolash eslatmasi', "Hurmatli ota-ona! Shartnoma imzolash muddati {sana} gacha. Joyingiz saqlanmoqda. Aloqa: {tel}. %S", {}),
 ]),
 ('B', 'DAVOMAT VA XAVFSIZLIK', 'Ota-ona', [
  ('B-01', "O'quvchi maktabga keldi", "{ism} bugun soat {vaqt} da maktabga keldi. %S", {}),
  ('B-02', "O'quvchi maktabdan chiqdi", "{ism} bugun soat {vaqt} da maktabdan chiqdi. %S", {}),
  ('B-03', "Ketma-ket darslarda yo'q", "Hurmatli ota-ona! {ism} bugun {son} ta darsda qatnashmadi. Direktor bilan bog'laning: {tel}. %S", {'tel': D}),
  ('B-04', 'Maktabga umuman kelmadi', "Hurmatli ota-ona! {ism} bugun maktabga kelmadi. Sabab haqida xabar bering: {tel}. %S", {}),
  ('B-05', 'Darsga kechikdi', "Hurmatli ota-ona! {ism} bugun darsga {daqiqa} daqiqa kechikdi. %S", {}),
  ('B-06', 'Maktab Gazeliga chiqdi', "{ism} soat {vaqt} da maktab Gazeliga chiqdi. %S", {}),
  ('B-07', 'Maktab Gazelidan tushdi', "{ism} soat {vaqt} da maktab Gazelidan tushdi. %S", {}),
  ('B-08', 'Gazel kechikmoqda', "Hurmatli ota-onalar! Maktab Gazeli yo'l harakati sababli {daqiqa} daqiqa kechikmoqda. %S", {}),
  ('B-09', 'Tibbiy xonaga murojaat', "Hurmatli ota-ona! {ism} tibbiy xonaga murojaat qildi. Holati barqaror. Sinf rahbari bilan bog'laning. %S", {}),
  ('B-10', "Shoshilinch aloqa so'rovi", "Hurmatli ota-ona! Iltimos, {ism} yuzasidan maktab bilan zudlik bilan bog'laning: {tel}. %S", {}),
  ('B-11', 'Farzandni olib ketish kodi', "Farzandingizni olib ketish uchun tasdiq kodi: {kod}. Kodni faqat ishonchli shaxsga ayting. %S", {}),
  ('B-12', 'Rejali xavfsizlik mashqi', "Hurmatli ota-onalar! {sana} kuni maktabda rejali xavfsizlik mashqi bo'ladi. Tashvishlanmang. %S", {}),
  ('B-13', 'Favqulodda holat xabari', "Hurmatli ota-onalar! Maktabda favqulodda holat bo'yicha chora ko'rilmoqda. O'quvchilar xavfsiz. Aloqa: {tel}. %S", {}),
 ]),
 ('C', 'JADVAL VA TASHKILIY XABARLAR', 'Ota-ona', [
  ('C-01', "Shanba kuni dars bo'lmaydi", "Hurmatli ota-onalar! {sana} shanba kuni darslar bo'lmaydi. Farzandingiz maktabga kelmaydi. %S", {}),
  ('C-02', "Darslar boshqa kunga ko'chirildi", "Hurmatli ota-onalar! {sana} kungi darslar {sana2} ga ko'chirildi. Jadval Durbin tizimida yangilandi. %S", {}),
  ('C-03', "Chorak ta'tili haqida eslatma", "Hurmatli ota-onalar! {chorak} ta'tili {sana} - {sana2} kunlari. Darslar {sana3} dan boshlanadi. %S", {}),
  ('C-04', "Ob-havo sababli dars bo'lmaydi", "Hurmatli ota-onalar! Ob-havo sababli {sana} kuni darslar bo'lmaydi. Yangiliklarni rasmiy sahifalarimizda kuzating. %S", {}),
  ('C-05', 'Qisqartirilgan dars kuni', "Hurmatli ota-onalar! {sana} kuni darslar qisqartirilgan jadvalda, soat {vaqt} da tugaydi. %S", {}),
  ('C-06', 'Yangi chorak boshlanishi', "Hurmatli ota-onalar! {chorak} {sana} dan boshlanadi. Darslar odatdagi jadval bo'yicha. %S", {}),
  ('C-07', 'Bayram sababli dam olish kuni', "Hurmatli ota-onalar! {bayram} munosabati bilan {sana} kuni darslar bo'lmaydi. %S", {}),
  ('C-08', "Yangi o'quv yili boshlanishi", "Hurmatli ota-onalar! Yangi o'quv yili {sana} dan boshlanadi. Batafsil ma'lumot Durbin tizimida. %S", {}),
 ]),
 ('D', 'AKADEMIK XABARLAR', 'Ota-ona', [
  ('D-01', "Chorak baholari e'lon qilindi", "Hurmatli ota-ona! {chorak} baholari Durbin tizimida e'lon qilindi. Ko'rish uchun tizimga kiring. %S", {}),
  ('D-02', 'Nazorat ishi haqida ogohlantirish', "Hurmatli ota-ona! {sana} kuni {fan} fanidan nazorat ishi bo'ladi. Tayyorgarlikni qo'llab-quvvatlang. %S", {}),
  ('D-03', 'Akademik yordam zarurligi', "Hurmatli ota-ona! {ism} {fan} fanida qo'shimcha yordamga muhtoj. Maktab direktori: {tel}. %S", {'tel': D}),
  ('D-04', "Qo'shimcha dars / konsultatsiya", "Hurmatli ota-ona! {ism} uchun {fan} fanidan qo'shimcha dars {sana} soat {vaqt} da. %S", {}),
  ('D-05', 'Olimpiada / tanlov natijasi', "Tabriklaymiz! {ism} {tanlov} da {orin} ni egalladi. Yutuqlaringiz davomli bo'lsin! %S", {}),
  ('D-06', "IELTS / SAT ro'yxatdan o'tish", "Hurmatli ota-ona! {imtihon} imtihoni {sana} kuni. Ro'yxat {sana2} gacha: {tel}. %S", {}),
  ('D-07', 'Imtihon natijasi', "Hurmatli ota-ona! {ism} ning {imtihon} natijasi: {natija}. Batafsil Durbin tizimida. %S", {}),
  ('D-08', 'Uy vazifasi (haftalik xulosa)', "Hurmatli ota-ona! {ism} bu hafta {son} ta uy vazifasini bajarmadi. Sinf rahbari: {tel}. %S", {}),
 ]),
 ('E', 'TARBIYA VA RIVOJLANISH', 'Ota-ona', [
  ('E-01', 'Ijobiy xabar (haftalik)', "Hurmatli ota-ona! {ism} bu hafta {yutuq} bilan ajralib turdi. Farzandingiz bilan faxrlaning! %S", {}),
  ('E-02', 'Rivojlanish kartasi tayyor', "Hurmatli ota-ona! {ism} ning oylik rivojlanish kartasi tayyor. Durbin tizimida ko'ring. %S", {}),
  ('E-03', "Reyting o'sishi", "Hurmatli ota-ona! {ism} ning maktab reytingi o'sdi. Joriy natija: {ball} ball. %S", {'son': '86'}),
  ('E-04', 'Adaptatsiya monitoringi natijasi', "Hurmatli ota-ona! {ism} ning adaptatsiya monitoringi yakunlandi. Psixolog bilan bog'laning: {tel}. %S", {}),
  ('E-05', "Intizom bo'yicha suhbat zarur", "Hurmatli ota-ona! {ism} yuzasidan sinf rahbari bilan suhbat zarur. Aloqa: {tel}. %S", {}),
 ]),
 ('F', 'OTA-ONA SERVISI VA ALOQA', 'Ota-ona', [
  ('F-01', "Ota-onalar yig'ilishi taklifi", "Hurmatli ota-onalar! {sinf} sinf ota-onalar yig'ilishi {sana} soat {vaqt} da bo'ladi. Kutib qolamiz. %S", {}),
  ('F-02', "Yig'ilish eslatmasi (24 soat)", "Hurmatli ota-onalar! Ertaga soat {vaqt} da ota-onalar yig'ilishi. Ishtirokingiz muhim. %S", {}),
  ('F-03', "Individual uchrashuv tasdig'i", "Hurmatli ota-ona! Uchrashuv {sana} soat {vaqt} ga belgilandi. O'zgarish bo'lsa: {tel}. %S", {}),
  ('F-04', 'Murojaat qabul qilindi', "Hurmatli ota-ona! Murojaatingiz qabul qilindi. Raqam: {raqam}. Javob {muddat} ichida beriladi. %S", {}),
  ('F-05', 'Murojaat hal qilindi', "Hurmatli ota-ona! {raqam} raqamli murojaatingiz hal qilindi. Savollar bo'lsa: {tel}. %S", {}),
  ('F-06', "So'rovnoma / sifat baholash", "Hurmatli ota-ona! Xizmat sifatini baholashda yordam bering: {havola}. Rahmat! %S", {}),
  ('F-07', 'Ota-onalar uchun seminar', "Hurmatli ota-onalar! {sana} soat {vaqt} da seminar: {mavzu}. Kutib qolamiz. %S", {}),
  ('F-08', 'Forma va kitoblar tarqatish', "Hurmatli ota-onalar! Maktab formasi va kitoblar {sana} dan beriladi. Aloqa: {tel}. %S", {}),
  ('F-09', "Ovqatlanish menyusi o'zgarishi", "Hurmatli ota-onalar! {sana} kuni ovqatlanish menyusi o'zgardi. Batafsil Durbin tizimida. %S", {}),
 ]),
 ('G', 'QABUL VA SHARTNOMA', 'Ota-ona / abituriyent ota-onasi', [
  ('G-01', 'Ariza qabul qilindi', "Hurmatli ota-ona! Arizangiz qabul qilindi. Menejerimiz {muddat} ichida bog'lanadi. %S", {}),
  ('G-02', 'Qabul imtihoni sanasi', "Hurmatli ota-ona! Qabul imtihoni {sana} soat {vaqt} da. Manzil: {manzil}. %S", {}),
  ('G-03', "Qabul natijasi: o'tdi", "Tabriklaymiz! {ism} qabul imtihonidan o'tdi. Hujjat topshirish uchun: {tel}. %S", {}),
  ('G-04', "Qabul natijasi: kutish ro'yxati", "Hurmatli ota-ona! {ism} kutish ro'yxatiga kiritildi. Joy bo'shasa xabar beramiz. %S", {}),
  ('G-05', 'Ochiq eshiklar kuni', "Hurmatli ota-onalar! {sana} soat {vaqt} da Ochiq eshiklar kuni. Ro'yxatdan o'ting: {tel}. %S", {}),
  ('G-06', 'Joy band qilish muddati', "Hurmatli ota-ona! {ism} uchun joy {sana} gacha saqlanadi. Tasdiqlash uchun: {tel}. %S", {}),
  ('G-07', "Hujjatlar to'liq emas", "Hurmatli ota-ona! Hujjatlar to'liq emas. Kerak: {hujjat}. Aloqa: {tel}. %S", {}),
 ]),
 ('H', 'XODIMLAR UCHUN', 'Maktab xodimi', [
  ('H-01', 'Pedagogik kengash', "Hurmatli xodim! {sana} soat {vaqt} da pedagogik kengash bo'ladi. Ishtirok majburiy. %S", {}),
  ('H-02', 'Navbatchilik eslatmasi', "Hurmatli xodim! {sana} kuni navbatchilik sizda. Boshlanish vaqti: {vaqt}. %S", {}),
  ('H-03', 'Malaka oshirish / attestatsiya', "Hurmatli xodim! {sana} soat {vaqt} da mashg'ulot. Mavzu: {mavzu}. %S", {}),
  ('H-04', "Ish tartibi o'zgarishi", "Hurmatli xodim! {sana} kuni maktab ish tartibi o'zgardi. Batafsil Durbin tizimida. %S", {}),
  ('H-05', 'Hisobot topshirish eslatmasi', "Hurmatli xodim! {sana} gacha hisobotni Durbin tizimiga kiriting. %S", {}),
 ]),
 ('I', 'TABRIKLAR', 'Ota-ona', [
  ('I-02', 'Bayram tabrigi (ota-ona)', "Hurmatli ota-onalar! {bayram} muborak bo'lsin. Oilangizga tinchlik, farzandlaringizga barokat tilaymiz. %S", {}),
  ('I-04', "O'quv yili yakuni", "Hurmatli ota-onalar! O'quv yili muvaffaqiyatli yakunlandi. Hamkorligingiz uchun rahmat! %S", {}),
 ]),
 ('J', 'TIZIM VA TEXNIK XABARLAR', 'Ota-ona', [
  ('J-01', 'Durbin tizimida nosozlik', "Hurmatli ota-onalar! Durbin tizimida vaqtinchalik texnik nosozlik yuz berdi. Mutaxassislar ishlamoqda. Uzr so'raymiz. %S", {}),
  ('J-02', 'Durbin tizimi tiklandi', "Hurmatli ota-onalar! Durbin tizimi qayta ishga tushdi. Barcha ma'lumotlar saqlangan. %S", {}),
  ('J-03', 'Rejali texnik ishlar', "Hurmatli ota-onalar! {sana} kuni soat {vaqt} da Durbin tizimida rejali texnik ishlar bo'ladi. %S", {}),
  ('J-04', 'Maktab telefoni ishlamayapti', "Hurmatli ota-onalar! Maktab telefoni vaqtincha ishlamayapti. Aloqa uchun: {tel2}. Telegram: {kanal}. %S", {}),
  ('J-05', 'Rasmiy kanalga ulanish', "Hurmatli ota-onalar! Maktab yangiliklarini rasmiy Telegram kanalimizda kuzating: {kanal}. %S", {}),
  ('J-06', 'Durbin tizimiga kirish kodi', "Durbin tizimiga kirish kodi: {kod}. Kodni hech kimga bermang. %S", {}),
  ('J-07', 'Parolni tiklash kodi', "Durbin parolini tiklash kodi: {kod}. Agar so'ramagan bo'lsangiz, e'tibor bermang. %S", {}),
 ]),
]

TOTAL = sum(len(b[3]) for b in BLOCKS)


def fill(tpl, ov):
    vals = dict(SAMPLE, **ov)
    return re.sub(r'\{(\w+)\}', lambda m: vals[m.group(1)], tpl)


# validate
for _, _, _, rows in BLOCKS:
    for code, _, tpl, ov in rows:
        t = tpl.replace('%S', SIG)
        gsm_len(t.replace('{', '(').replace('}', ')'))
        n = gsm_len(fill(t, ov))
        assert n <= 160, (code, n)

# ---------------------------------------------------------------- HTML


def read(p):
    return open(p, encoding='utf-8').read()


def svg_inline(path, fill=None):
    s = read(path)
    s = re.sub(r'<\?xml[^>]*>', '', s)
    if fill:
        s = re.sub(r'fill:\s*#[0-9a-fA-F]+', f'fill: {fill}', s)
    return s


logo_white = svg_inline(f'{BRAND}/Logotype/SVG/Logo white.svg')
el1 = svg_inline(f'{BRAND}/Patterns & graphic elements/SVG/Element 1.svg', '#ff4a4a')
el3 = svg_inline(f'{BRAND}/Patterns & graphic elements/SVG/Element 3.svg', '#ff4a4a')
pattern = svg_inline(f'{BRAND}/Patterns & graphic elements/SVG/Pattern 1.svg', '#ff4a4a')
# give each inline svg a unique class namespace to avoid .cls-1 collisions
def uniq(svg, tag):
    return svg.replace('cls-1', f'{tag}-c')
logo_white, el1, el3, pattern = uniq(logo_white, 'lw'), uniq(el1, 'e1'), uniq(el3, 'e3'), uniq(pattern, 'pt')

FONT_CSS = read(f'{FONTS}/geist-embed.css') + '\n' + read(f'{FONTS}/inter-embed.css')

BASE_CSS = """
:root{--red:#dd1717;--red-l:#ff4a4a;--white:#fff;--black:#070707;--raised:#f4f4f4;
--muted:#5a5a5a;--border:#dcdcdc;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff;color:var(--black);font-family:Geist,Inter,sans-serif;
-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-size:9.2pt;line-height:1.45}
"""

COVER_CSS = """
@page{size:A4;margin:0}
.cover{width:210mm;height:297mm;background:var(--red);color:#fff;position:relative;overflow:hidden;
padding:22mm 20mm}
.cover .logo svg{height:17mm;width:auto;display:block}
.cover .shape1{position:absolute;right:-38mm;top:62mm;width:128mm}
.cover .shape3{position:absolute;right:20mm;top:20mm;width:34mm}
.cover .pattern{position:absolute;left:20mm;bottom:22mm;width:34mm;opacity:1}
.cover .shape1 svg,.cover .shape3 svg,.cover .pattern svg{width:100%;height:auto;display:block}
.cover .overline{position:absolute;top:92mm;left:20mm;font-weight:500;font-size:10pt;letter-spacing:.14em;text-transform:uppercase}
.cover h1{position:absolute;top:101mm;left:20mm;font-weight:700;font-size:44pt;line-height:1.0;letter-spacing:-.02em;width:140mm}
.cover .sub{position:absolute;top:151mm;left:20mm;font-weight:500;font-size:13pt;width:120mm}
.cover .meta{position:absolute;left:66mm;right:20mm;bottom:22mm;border-top:1.2pt solid #fff}
.cover .meta table{width:100%;border-collapse:collapse;font-size:9pt}
.cover .meta td{padding:2.1mm 0;border-bottom:.5pt solid rgba(255,255,255,.55);vertical-align:top}
.cover .meta td:first-child{width:36%;font-weight:400}
.cover .meta td:last-child{font-weight:700}
.cover .conf{position:absolute;left:66mm;bottom:13mm;font-size:7.5pt}
"""

BODY_CSS = """
@page{size:A4;margin:27mm 16mm 20mm 16mm}
h2{font-weight:700;font-size:15pt;letter-spacing:-.01em;margin:0 0 3.2mm;display:flex;align-items:baseline;gap:3mm;
break-after:avoid}
h2 .num{color:var(--red);font-weight:700;font-size:15pt;font-variant-numeric:tabular-nums}
section{margin-bottom:8mm}
p{margin:0 0 2.6mm;max-width:172mm}
table{width:100%;border-collapse:collapse}
thead{display:table-header-group}
th{white-space:nowrap;background:var(--black);color:#fff;font-weight:500;font-size:8pt;text-align:left;padding:2mm 2.4mm;
letter-spacing:.02em}
td{padding:2mm 2.4mm;border-bottom:.5pt solid var(--border);vertical-align:top}
tr{break-inside:avoid}
tbody tr:nth-child(even) td{background:var(--raised)}
.kv td:first-child{width:33%;font-weight:500}
.mono{font-variant-numeric:tabular-nums}
.var{font-weight:700;color:var(--red);white-space:nowrap}
.note{background:var(--black);color:#fff;padding:3.4mm 4mm;font-size:8.4pt;margin-top:3.2mm;break-inside:avoid}
.note b{color:var(--red-l)}
.contacts{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1.2pt solid var(--black);break-inside:avoid}
.contacts>div{padding:3mm 3mm 3mm 0;border-bottom:.5pt solid var(--border)}
.contacts .l{font-size:7.6pt;font-weight:500;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.contacts .v{font-size:11pt;font-weight:700;margin-top:1mm;white-space:nowrap}
.contacts .u{font-size:7.8pt;color:var(--muted);margin-top:.6mm}
.block{margin-top:7mm}
.bhead{display:flex;align-items:center;gap:3.2mm;margin-bottom:2.4mm;break-after:avoid}
.bhead .letter{width:9mm;height:9mm;background:var(--red);color:#fff;font-weight:700;font-size:13pt;
display:flex;align-items:center;justify-content:center;flex:none}
.bhead .t{font-weight:700;font-size:11.5pt;letter-spacing:.01em}
.bhead .m{font-size:8pt;color:var(--muted);margin-top:.3mm}
.sms td.code{font-weight:700;color:var(--red);width:13mm;white-space:nowrap}
.sms td.title{width:36mm;font-weight:500}
.sms td.txt .tpl{font-weight:400}
.sms td.txt .tpl .v{color:var(--red);font-weight:500}
.sms td.txt .ex{color:var(--muted);font-size:8pt;margin-top:1.2mm}
.sms td.txt .ex b{font-weight:500;color:var(--black)}
.sms td.len{width:17mm;text-align:right;white-space:nowrap}
.sms td.len .n{font-weight:700}
.bar{height:1.2mm;background:var(--border);margin-top:1.4mm;width:100%}
.bar i{display:block;height:100%;background:var(--red)}
.sms th.len{text-align:right}
.chg{font-size:6.8pt;font-weight:500;color:#fff;background:var(--black);padding:.3mm 1.4mm;margin-left:1.4mm;
white-space:nowrap;vertical-align:1px}
.mod td{height:9mm;vertical-align:middle}
.mod td.c{font-weight:700;color:var(--red);width:10mm}
.mod td.n{text-align:center;width:22mm}
.mod td.box{width:24mm}
.mod td.box span{display:inline-block;width:4.2mm;height:4.2mm;border:1pt solid var(--black)}
.mod tr.total td{background:var(--black)!important;color:#fff;font-weight:700;border:none}
.signs{display:grid;grid-template-columns:1fr 1fr;gap:10mm;margin-top:9mm;break-inside:avoid}
.signs .s{border-top:1.2pt solid var(--black);padding-top:3mm}
.signs .h{font-weight:700;font-size:10pt;margin-bottom:4mm}
.signs .row{display:flex;gap:2mm;margin-bottom:4.5mm;font-size:9pt}
.signs .row span:first-child{width:26mm;color:var(--muted)}
.signs .row .line{flex:1;border-bottom:.6pt solid var(--black)}
.signs .row b{font-weight:700}
"""


def hl_tpl(tpl):
    t = esc(tpl.replace('%S', SIG))
    return re.sub(r'\{(\w+)\}', r'<span class="v">{\1}</span>', t)


CHANGED = {'B-03', 'B-06', 'B-07', 'B-08', 'B-09', 'D-03'}


def cover_html():
    meta = [
        ('Hujjat kodi', 'TT-IT-SMS-01'), ('Versiya', '1.0'), ('Sana', DOC_DATE),
        ('Shablonlar soni', f'{TOTAL} ta'), ('Alifbo / kodlash', 'Lotin, GSM-7'),
        ('Maksimal uzunlik', '160 belgi = 1 SMS'), ('Tizim', 'Durbin LMS/CRM/ERP'),
        ('Tasdiqlovchi', f'Maktab direktori: {DIRECTOR}'),
    ]
    rows = ''.join(f'<tr><td>{P(a)}</td><td>{P(b)}</td></tr>' for a, b in meta)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}{BASE_CSS}{COVER_CSS}</style></head>
<body><div class="cover">
<div class="logo">{logo_white}</div>
<div class="shape1">{el1}</div>
<div class="shape3">{el3}</div>
<div class="pattern">{pattern}</div>
<div class="overline">Xiva shahri, Xorazm viloyati</div>
<h1>SMS shablonlari reyestri</h1>
<div class="sub">{P('Operator moderatsiyasi uchun rasmiy hujjat')}</div>
<div class="meta"><table>{rows}</table></div>
<div class="conf">{P("Maxfiy — ichki foydalanish va SMS-operator moderatsiyasi uchun")}</div>
</div></body></html>"""


INTRO5 = "Har bir shablon uchun: shablon matni (o'zgaruvchilar bilan) va namunaviy to'ldirilgan matn keltirilgan. \"Belgi\" ustunida namunaviy matnning GSM-7 bo'yicha uzunligi ko'rsatilgan. Barcha shablonlar 160 belgi chegarasida, ya'ni 1 SMS."


NOTE2 = "SMS matnlarida \"o'\" va \"g'\" harflari uchun faqat to'g'ri apostrof (') ishlatilgan. Egri apostrof (U+02BB) GSM-7 jadvalida mavjud emas va xabarni UCS-2 kodlashga o'tkazib, uzunlik chegarasini 70 belgiga tushiradi."


def body_html():
    h = []
    h.append(f"""<section><h2><span class="num">01</span>{P('Hujjat maqsadi')}</h2>
<p>{P(f"Ushbu hujjat {SCHOOL} tomonidan Durbin tizimi orqali ota-onalar va maktab xodimlariga yuboriladigan barcha SMS-xabar shablonlarini o'z ichiga oladi. Hujjat SMS-operator (agregator) tomonidan oldindan moderatsiyadan o'tkazilishi va tasdiqlanishi uchun taqdim etiladi.")}</p>
<p>{P("Xabarlarni yuborish vaqti, chastotasi va qabul qiluvchilar ro'yxati maktab tomonidan mustaqil belgilanadi. Operatordan faqat shablon matnlarini tasdiqlash so'raladi.")}</p>
<p>{P("Barcha shablonlar axborot xarakteriga ega bo'lib, maktab va ota-ona o'rtasidagi ta'lim xizmati shartnomasi doirasida yuboriladi. Reklama xarakteridagi xabarlar ushbu reyestrga kiritilmagan.")}</p>
</section>""")

    params = [
        ('Alifbo', "Lotin (o'zbek tili)"),
        ('Kodlash', 'GSM-7 (7-bit). Kirill va Unicode belgilar ishlatilmaydi'),
        ('Bir xabar uzunligi', 'Maksimal 160 belgi = 1 SMS segment'),
        ('Apostrof belgisi', "SMS matnida faqat to'g'ri apostrof ' (U+0027). Egri apostrof taqiqlanadi"),
        ('Taqiqlangan belgilar', 'Kirill harflari, en-dash, uch nuqta, № belgisi, gradus belgisi'),
        ('Ikki barobar sanaladigan belgilar', '[ ] { } \\ ~ ^ | — shablon matnlarida ishlatilmagan'),
        ("Jo'natuvchi nomi (Sender ID)", 'NATIJA (alfanumerik, tasdiqlash talab etiladi)'),
        ("O'zgaruvchilar formati", 'Jingalak qavs ichida: {ism}, {summa}, {sana}'),
        ('Jami shablonlar', f'{TOTAL} ta, {len(BLOCKS)} ta blokda'),
        ('Segment tekshiruvi', 'Har bir shablon namunaviy qiymatlar bilan tekshirilgan: 1 SMS'),
    ]
    rows = ''.join(f'<tr><td>{P(a)}</td><td>{esc(b) if "U+0027" in b else P(b)}</td></tr>' for a, b in params)
    h.append(f"""<section><h2><span class="num">02</span>{P('Umumiy texnik parametrlar')}</h2>
<table class="kv"><thead><tr><th>Parametr</th><th>Qiymat</th></tr></thead><tbody>{rows}</tbody></table>
<div class="note"><b>Diqqat:</b> {esc(NOTE2)}</div>
</section>""")

    contacts = [
        ('Maktab (asosiy)', TEL_MAIN, 'Umumiy aloqa, {tel}'),
        ('Buxgalteriya', TEL_BUX, "To'lov masalalari: A-01, A-03, A-06"),
        ('Maktab direktori', TEL_DIR, 'B-03, D-03'),
        ('Telegram kanal', TG, '{kanal}, {havola}'),
    ]
    cc = ''.join(f'<div><div class="l">{P(l)}</div><div class="v">{esc(v)}</div><div class="u">{P(u)}</div></div>' for l, v, u in contacts)
    h.append(f"""<section style="break-inside:avoid"><h2><span class="num">03</span>{P("Aloqa ma'lumotlari")}</h2>
<p>{P("Shablonlardagi {tel}, {tel2} va {kanal} o'zgaruvchilari quyidagi rasmiy raqam va manzillar bilan to'ldiriladi.")}</p>
<div class="contacts">{cc}</div></section>""")

    rows = ''.join(f'<tr><td class="var">{esc(a)}</td><td>{P(b)}</td><td class="mono">{c}</td><td>{esc(d)}</td></tr>'
                   for a, b, c, d in VARIABLES)
    h.append(f"""<section><h2><span class="num">04</span>{P("O'zgaruvchilar ro'yxati")}</h2>
<p>{P("Quyidagi o'zgaruvchilar yuborish vaqtida Durbin tizimi tomonidan avtomatik to'ldiriladi. Maksimal uzunlik tizim darajasida cheklangan.")}</p>
<table><thead><tr><th>{P("O'zgaruvchi")}</th><th>Mazmuni</th><th>Maks. belgi</th><th>Namunaviy qiymat</th></tr></thead><tbody>{rows}</tbody></table>
</section>""")

    h.append(f"""<section style="margin-bottom:0"><h2><span class="num">05</span>{P('SMS shablonlari')}</h2>
<p>{P(INTRO5)}</p>""")
    for letter, name, rcpt, rows in BLOCKS:
        trs = []
        for code, title, tpl, ov in rows:
            sample = fill(tpl.replace('%S', SIG), ov)
            n = gsm_len(sample)
            pct = n / 160 * 100
            trs.append(f"""<tr><td class="code">{code}</td><td class="title">{P(title)}</td>
<td class="txt"><div class="tpl">{hl_tpl(tpl)}</div><div class="ex"><b>Namuna:</b> {esc(sample)}</div></td>
<td class="len"><span class="n">{n}</span><div class="bar"><i style="width:{pct:.1f}%"></i></div></td></tr>""")
        h.append(f"""<div class="block"><div class="bhead"><div class="letter">{letter}</div><div>
<div class="t">Blok {letter} — {P(name)}</div><div class="m">{P(f'Qabul qiluvchi: {rcpt}')} · Shablonlar: {len(rows)} ta</div></div></div>
<table class="sms"><thead><tr><th>Kod</th><th>Xabar holati</th><th>SMS matni va namuna</th><th class="len">Belgi</th></tr></thead>
<tbody>{''.join(trs)}</tbody></table></div>""")
    h.append('</section>')

    mrows = ''.join(f'<tr><td class="c">{l}</td><td>{P(n)}</td><td class="n mono">{len(r)}</td><td class="box"><span></span></td><td></td></tr>'
                    for l, n, _, r in BLOCKS)
    h.append(f"""<section style="break-before:page"><h2><span class="num">06</span>{P('Moderatsiya natijasi')} <span style="font-weight:400;font-size:10pt;color:var(--muted)">{P("(operator to'ldiradi)")}</span></h2>
<table class="mod"><thead><tr><th>Blok</th><th>Nomi</th><th style="text-align:center">Shablonlar</th><th>Tasdiqlandi</th><th>Izoh / rad etish sababi</th></tr></thead>
<tbody>{mrows}<tr class="total"><td></td><td>JAMI</td><td class="n mono">{TOTAL}</td><td></td><td></td></tr></tbody></table>
<div class="signs">
<div class="s"><div class="h">{esc(SCHOOL.upper())}</div>
<div class="row"><span>Maktab direktori</span><b>{DIRECTOR}</b></div>
<div class="row"><span>Imzo</span><span class="line"></span></div>
<div class="row"><span>Sana</span><span class="line"></span></div></div>
<div class="s"><div class="h">SMS-OPERATOR (AGREGATOR)</div>
<div class="row"><span>{P("Mas'ul shaxs")}</span><span class="line"></span></div>
<div class="row"><span>Imzo</span><span class="line"></span></div>
<div class="row"><span>Sana</span><span class="line"></span></div></div>
</div></section>""")

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}{BASE_CSS}{BODY_CSS}</style></head>
<body>{''.join(h)}</body></html>"""


# ---------------------------------------------------------------- render
tmp = os.path.join(HERE, 'build')
os.makedirs(tmp, exist_ok=True)
open(f'{tmp}/cover.html', 'w').write(cover_html())
open(f'{tmp}/body.html', 'w').write(body_html())

with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    pg = br.new_page()
    for name in ('cover', 'body'):
        pg.goto(f'file://{tmp}/{name}.html')
        pg.wait_for_load_state('networkidle')
        pg.evaluate('document.fonts.ready')
        pg.pdf(path=f'{tmp}/{name}.pdf', format='A4', print_background=True, prefer_css_page_size=True)
    br.close()

# ---------------------------------------------------------------- stamp header/footer + merge
doc = pymupdf.open(f'{tmp}/cover.pdf')
body = pymupdf.open(f'{tmp}/body.pdf')
doc.insert_pdf(body)
logo = pymupdf.open(f'{BRAND}/Logotype/PDF/Logo colored.pdf')
MM = 72 / 25.4
RED = (221 / 255, 23 / 255, 23 / 255)
BLACK = (7 / 255, 7 / 255, 7 / 255)
MUTED = (0x5a / 255,) * 3
LINE = (0xdc / 255,) * 3
total = doc.page_count
for i in range(1, total):
    pg = doc[i]
    pg.insert_font(fontname='G4', fontfile=f'{FONTS}/geist-400.ttf')
    pg.insert_font(fontname='G5', fontfile=f'{FONTS}/geist-500.ttf')
    pg.insert_font(fontname='G7', fontfile=f'{FONTS}/geist-700.ttf')
    W = pg.rect.width
    L, R = 16 * MM, W - 16 * MM
    # header
    lr = logo[0].rect
    h = 8.2 * MM
    w = h * lr.width / lr.height
    pg.show_pdf_page(pymupdf.Rect(L, 11 * MM, L + w, 11 * MM + h), logo, 0)
    f5 = pymupdf.Font(fontfile=f'{FONTS}/geist-500.ttf')
    f4 = pymupdf.Font(fontfile=f'{FONTS}/geist-400.ttf')
    t1 = 'SMS SHABLONLARI REYESTRI'
    t2 = 'TT-IT-SMS-01  ·  v1.0'
    pg.insert_text((R - f5.text_length(t1, 7.6), 14.2 * MM), t1, fontname='G5', fontsize=7.6, color=BLACK)
    pg.insert_text((R - f4.text_length(t2, 7.2), 18.2 * MM), t2, fontname='G4', fontsize=7.2, color=MUTED)
    pg.draw_line((L, 21.5 * MM), (R, 21.5 * MM), color=BLACK, width=1.0)
    # footer
    y = pg.rect.height - 11 * MM
    pg.draw_line((L, y - 4.2 * MM), (R, y - 4.2 * MM), color=LINE, width=0.5)
    ft = f'Maxfiy - ichki foydalanish uchun  ·  {DOC_DATE}'
    pg.insert_text((L, y), ft, fontname='G4', fontsize=7.2, color=MUTED)
    pn = f'{i + 1}-bet'
    f7 = pymupdf.Font(fontfile=f'{FONTS}/geist-700.ttf')
    tw = f7.text_length(pn, 7.6)
    pg.insert_text((R - tw, y), pn, fontname='G7', fontsize=7.6, color=BLACK)
    pg.draw_circle((R - tw - 2.6 * MM, y - 0.95 * MM), 1.05 * MM, color=RED, fill=RED)

doc.set_metadata({'title': 'NATIJA maktabi — SMS shablonlari reyestri (TT-IT-SMS-01)',
                  'author': 'NATIJA maktabi', 'subject': 'SMS shablonlari reyestri', 'creator': 'NATIJA maktabi'})
doc.save(OUT, garbage=4, deflate=True)
print('OK', OUT, 'pages', total, 'templates', TOTAL)

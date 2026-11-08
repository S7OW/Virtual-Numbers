import os
import random
import sqlite3
import logging
from html import escape

from babel import Locale
from telegram import InlineKeyboardButton as B, InlineKeyboardMarkup as M, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
)

logging.basicConfig(level=logging.INFO)

# ================= الإعدادات (عدّل القيم هنا مباشرة) =================
BOT_TOKEN = "9232108918:AAHv_SMhG7tUivv2mHQJ-1NZ5jFKGv-1JkY"          # من @BotFather
ADMIN_ID = 2034648592                          # ايديك الرقمي من @userinfobot
USDT_ADDRESS = "0x778A4416eCe521Db1809260218BCa2DD850B28F5"    # عنوان محفظتك
USDT_NETWORK = "BEP20"
MARKUP = 1.5                          # ربحك: سعر القائمة × هذا الرقم
BRAND = "KYRO"                        # اسم مشروعك
ALWAYS_AVAILABLE = True               # True: كل الدول تظهر متاحة، والرقم الفعلي يُسلَّم بعد الدفع (من المخزون أو منك يدويا)
CONTACT_TELEGRAM = ""                 # يوزرك في تليجرام بدون @ (مثال: myname)
CONTACT_INSTAGRAM = "jrvwe"           # يوزر انستغرام بدون @
CONTACT_EMAIL = "q4n.m08@gmail.com"   # بريدك
# ====================================================================

TOKEN = BOT_TOKEN
ADMIN = int(ADMIN_ID)
WALLET = USDT_ADDRESS
NETWORK = USDT_NETWORK

APPS = ["WhatsApp", "Telegram", "Instagram", "Facebook", "TikTok", "Google"]
PER_PAGE = 12
SHOWN_NUMBERS = 6
HTML = ParseMode.HTML
LANGS = {"ar": "العربية", "fr": "Français", "en": "English"}
LINE = "━━━━━━━━━━━━━━━━━━━━"

# ---------- النصوص (3 لغات، رسمية وبدون إيموجي) ----------
T = {
    "ar": {
        "welcome": "خدمة الأرقام الافتراضية لاستقبال رموز التحقق.\nتسليم فوري  |  الدفع بعملة USDT\n\nيرجى اختيار التطبيق للمتابعة.",
        "pick_country": "اختر الدولة",
        "soldout_tag": "نفد",
        "pick_number": "اختر رقمًا",
        "numbers_note": "الأرقام المعروضة للاطلاع فقط. يُسلَّم رقم فعلي من الدولة المختارة بعد تأكيد الدفع.",
        "more_numbers": "أرقام أخرى",
        "sold_out": "نعتذر، لا توجد أرقام متوفرة لهذه الدولة حاليًا.",
        "back": "رجوع",
        "home": "الرئيسية",
        "language": "اللغة",
        "support_btn": "الدعم والتواصل",
        "support_msg": "<b>الدعم والتواصل</b>\n{line}\nيسعدنا مساعدتك. يمكنك التواصل معنا عبر:\n\nالبريد الإلكتروني: <code>{email}</code>\n\nأو عبر الأزرار أدناه.",
        "order": (
            "<b>{brand}</b>\n{line}\n<b>طلب رقم {oid}</b>\n\n"
            "التطبيق:  {app}\nالدولة:  {country}\nالرقم المختار:  <code>{shown}</code>\nالمبلغ:  <b>{amount} USDT</b>\n{line}\n"
            "الشبكة:  <b>{network}</b>\nعنوان المحفظة:\n<code>{wallet}</code>\n{line}\n"
            "يرجى التحويل على الشبكة المذكورة فقط. بعد التحويل اضغط «تم الدفع» ثم أرسل رقم العملية (TXID) أو لقطة شاشة.\n"
            "يُسلَّم الرقم الفعلي بعد تأكيد الدفع."
        ),
        "paid_btn": "تم الدفع",
        "cancel_btn": "إلغاء الطلب",
        "cancelled": "تم إلغاء الطلب.",
        "send_proof": "يرجى إرسال رقم العملية (TXID) أو لقطة شاشة للدفع.",
        "proof_ok": "تم استلام إثبات الدفع.\nجارٍ المراجعة، وسيصلكم الرقم خلال دقائق.",
        "confirmed": (
            "<b>تم تأكيد الدفع</b>\n{line}\nرقمكم:\n<code>{phone}</code>\n{line}\n"
            "يرجى استخدام الرقم في التطبيق، ثم الضغط على الزر أدناه لطلب الكود."
        ),
        "code_btn": "طلب الكود",
        "code_again_btn": "طلب كود آخر",
        "code_wait": "تم إشعار الفريق، وسيصلكم الكود خلال لحظات.",
        "code_msg": "<b>رمز التحقق</b>\n{line}\n<code>{code}</code>",
        "rejected": "تعذّر تأكيد الدفع للطلب رقم {oid}.\nإن كان هناك خطأ، يرجى التواصل مع الدعم.",
    },
    "fr": {
        "welcome": "Service de numéros virtuels pour la réception de codes de vérification.\nLivraison instantanée  |  Paiement en USDT\n\nVeuillez sélectionner une application pour continuer.",
        "pick_country": "Sélectionnez le pays",
        "soldout_tag": "épuisé",
        "pick_number": "Sélectionnez un numéro",
        "numbers_note": "Les numéros affichés le sont à titre indicatif. Un numéro réel du pays choisi vous est attribué après confirmation du paiement.",
        "more_numbers": "Autres numéros",
        "sold_out": "Désolé, aucun numéro n'est disponible pour ce pays actuellement.",
        "back": "Retour",
        "home": "Accueil",
        "language": "Langue",
        "support_btn": "Support et contact",
        "support_msg": "<b>Support et contact</b>\n{line}\nNous sommes à votre disposition. Vous pouvez nous joindre via :\n\nE-mail : <code>{email}</code>\n\nOu à l'aide des boutons ci-dessous.",
        "order": (
            "<b>{brand}</b>\n{line}\n<b>Commande n° {oid}</b>\n\n"
            "Application :  {app}\nPays :  {country}\nNuméro sélectionné :  <code>{shown}</code>\nMontant :  <b>{amount} USDT</b>\n{line}\n"
            "Réseau :  <b>{network}</b>\nAdresse du portefeuille :\n<code>{wallet}</code>\n{line}\n"
            "Veuillez effectuer le virement uniquement sur le réseau indiqué. Ensuite, appuyez sur « Paiement effectué » puis envoyez l'identifiant de transaction (TXID) ou une capture d'écran.\n"
            "Le numéro réel est attribué après confirmation du paiement."
        ),
        "paid_btn": "Paiement effectué",
        "cancel_btn": "Annuler la commande",
        "cancelled": "La commande a été annulée.",
        "send_proof": "Veuillez envoyer l'identifiant de transaction (TXID) ou une capture d'écran du paiement.",
        "proof_ok": "Preuve de paiement reçue.\nVérification en cours, votre numéro vous sera communiqué sous quelques minutes.",
        "confirmed": (
            "<b>Paiement confirmé</b>\n{line}\nVotre numéro :\n<code>{phone}</code>\n{line}\n"
            "Veuillez l'utiliser dans l'application, puis appuyer sur le bouton ci-dessous pour demander le code."
        ),
        "code_btn": "Demander le code",
        "code_again_btn": "Demander un autre code",
        "code_wait": "Notre équipe a été informée, le code vous parviendra dans un instant.",
        "code_msg": "<b>Code de vérification</b>\n{line}\n<code>{code}</code>",
        "rejected": "Le paiement de la commande n° {oid} n'a pas pu être confirmé.\nEn cas d'erreur, veuillez contacter le support.",
    },
    "en": {
        "welcome": "Virtual number service for receiving verification codes.\nInstant delivery  |  Payment in USDT\n\nPlease select an application to continue.",
        "pick_country": "Select a country",
        "soldout_tag": "sold out",
        "pick_number": "Select a number",
        "numbers_note": "Numbers shown are for preview only. A real number from the selected country is assigned after payment is confirmed.",
        "more_numbers": "More numbers",
        "sold_out": "Sorry, no numbers are currently available for this country.",
        "back": "Back",
        "home": "Home",
        "language": "Language",
        "support_btn": "Support and contact",
        "support_msg": "<b>Support and contact</b>\n{line}\nWe are glad to help. You can reach us via:\n\nEmail: <code>{email}</code>\n\nOr use the buttons below.",
        "order": (
            "<b>{brand}</b>\n{line}\n<b>Order #{oid}</b>\n\n"
            "Application:  {app}\nCountry:  {country}\nSelected number:  <code>{shown}</code>\nAmount:  <b>{amount} USDT</b>\n{line}\n"
            "Network:  <b>{network}</b>\nWallet address:\n<code>{wallet}</code>\n{line}\n"
            "Please transfer on the stated network only. Then tap “I have paid” and send the transaction ID (TXID) or a screenshot.\n"
            "The real number is assigned after payment is confirmed."
        ),
        "paid_btn": "I have paid",
        "cancel_btn": "Cancel order",
        "cancelled": "The order has been cancelled.",
        "send_proof": "Please send the transaction ID (TXID) or a screenshot of the payment.",
        "proof_ok": "Payment proof received.\nReview in progress, your number will be sent within minutes.",
        "confirmed": (
            "<b>Payment confirmed</b>\n{line}\nYour number:\n<code>{phone}</code>\n{line}\n"
            "Please use it in the app, then tap the button below to request the code."
        ),
        "code_btn": "Request code",
        "code_again_btn": "Request another code",
        "code_wait": "Our team has been notified, your code will arrive shortly.",
        "code_msg": "<b>Verification code</b>\n{line}\n<code>{code}</code>",
        "rejected": "Payment for order #{oid} could not be confirmed.\nIf this is a mistake, please contact support.",
    },
}

NAMES = {l: Locale(l).territories for l in LANGS}

# ---------- البيانات ----------
COUNTRIES_TXT = """
UZ 998 0.45
BD 880 0.20
SA 966 0.70
IT 39 1
MX 52 0.40
KZ 7 0.80
UA 380 1.7
YE 967 0.20
LV 371 1
KG 996 0.60
US 1 0.25
TR 90 0.70
CO 57 0.22
ZW 263 0.25
AR 54 0.40
GB 44 0.40
HK 852 0.25
TH 66 0.20
WS 685 0.60
TN 216 0.50
MA 212 0.30
LB 961 0.40
MZ 258 0.15
VN 84 0.50
GH 233 0.10
IR 98 0.40
AE 971 1.3
ML 223 0.10
PG 675 0.40
NE 227 0.10
PE 51 0.30
TZ 255 0.25
GT 502 0.20
SY 963 0.40
PS 970 0.60
KH 855 0.30
PR 1787 0.40
SZ 268 0.45
TL 670 0.50
KR 82 2.2
SE 46 0.75
EE 372 0.50
FI 358 0.60
LA 856 0.60
NG 234 0.20
IL 972 0.30
PH 63 0.35
IE 353 0.40
AT 43 0.60
RS 381 0.80
RO 40 0.30
SI 386 0.85
ET 251 0.25
NI 505 0.15
PY 595 0.70
HU 36 0.20
UG 256 0.30
MN 976 0.85
BY 375 1
CA 1 0.25
ZM 260 0.30
SO 252 0.30
PL 48 0.50
KE 254 0.20
SV 503 0.40
MM 95 0.20
LY 218 0.45
FJ 679 0.50
NU 683 3
TO 676 0.50
CR 506 0.20
HN 504 0.30
JP 81 0.50
NO 47 0.80
AU 61 1.2
CH 41 1.7
CL 56 0.20
BJ 229 0.20
BI 257 0.40
CU 53 0.40
PA 507 0.20
QA 974 1.2
KW 965 1.4
TG 228 0.25
AM 374 0.50
AO 244 0.45
TD 235 0.30
DZ 213 0.35
SG 65 2
TM 993 0.50
BM 14 0.40
DE 49 0.80
MV 960 0.60
CZ 420 0.80
MD 373 1
BE 32 1
NZ 64 0.80
KI 686 0.85
MO 853 1
SB 677 0.50
AW 297 1
DJ 253 0.60
AL 355 0.30
MC 377 1
KM 269 0.40
IS 354 0.70
BA 387 0.60
DO 1 0.45
EC 593 0.15
TT 1 0.50
JM 1 0.25
HT 509 0.25
AZ 994 1
BG 359 0.70
LU 352 0.85
CV 238 0.60
SC 248 0.50
UY 598 0.40
GD 1 0.60
AI 1 0.70
KY 1 0.80
VC 1 0.30
LC 1 0.50
GP 590 0.40
MU 230 0.30
SR 597 0.70
LS 266 0.30
GY 592 0.50
DM 1 0.30
NA 264 0.30
BB 1 0.40
BZ 501 0.70
GA 241 0.30
ZA 27 0.35
BT 975 1
CF 236 0.25
PW 680 1.2
LT 370 1
GR 30 0.70
GL 299 0.50
MR 222 0.40
GU 1 0.40
CK 682 3
FK 500 8
SS 211 0.20
MG 261 0.05
RU 7 1.2
PT 351 0.60
TJ 992 0.50
EG 20 0.40
IQ 964 1.2
VE 58 0.60
FR 33 1
NL 31 1
ES 34 1
SN 221 0.40
IN 91 0.25
GE 995 1
SL 232 0.20
PK 92 0.25
AF 93 0.25
LK 94 0.40
JO 962 0.70
ID 62 0.20
SD 249 0.15
TW 886 1
CN 86 0.25
MW 265 0.50
MY 60 0.55
NP 977 0.35
HR 385 0.70
BO 591 0.80
DK 45 1
OM 968 1
GN 224 0.30
MT 356 1
BH 973 1.8
BR 55 0.50
CM 237 0.20
CI 225 0.50
ST 239 0.50
BW 267 0.40
CG 242 0.50
BS 1 0.60
"""

COUNTRIES = {}  # iso -> (dial, base_price)
for line in COUNTRIES_TXT.splitlines():
    parts = line.split()
    if len(parts) == 3:
        COUNTRIES[parts[0]] = (parts[1], float(parts[2]))


def _open_db():
    for path in (os.path.join(os.path.expanduser("~"), "numbers_bot.db"), "numbers_bot.db"):
        try:
            return sqlite3.connect(path, check_same_thread=False)
        except sqlite3.Error:
            continue
    return sqlite3.connect(":memory:", check_same_thread=False)


db = _open_db()
db.executescript("""
CREATE TABLE IF NOT EXISTS numbers(
  id INTEGER PRIMARY KEY AUTOINCREMENT, app TEXT, cc TEXT, phone TEXT, status TEXT DEFAULT 'free');
CREATE TABLE IF NOT EXISTS orders(
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, app TEXT, cc TEXT,
  price REAL, status TEXT, number_id INTEGER, phone TEXT);
CREATE TABLE IF NOT EXISTS prices(cc TEXT PRIMARY KEY, price REAL);
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, lang TEXT);
""")
db.commit()
try:
    db.execute("ALTER TABLE orders ADD COLUMN phone TEXT")
    db.commit()
except sqlite3.OperationalError:
    pass


def get_lang(uid):
    r = db.execute("SELECT lang FROM users WHERE id=?", (uid,)).fetchone()
    return r[0] if r else None


def set_lang(uid, lang):
    db.execute("INSERT OR REPLACE INTO users(id, lang) VALUES(?,?)", (uid, lang))
    db.commit()


def tr(uid, key, **kw):
    lang = get_lang(uid) or "en"
    return T[lang][key].format(brand=BRAND, line=LINE, **kw)


def cname(cc, lang):
    return NAMES[lang].get(cc, cc).split(" (")[0]


def flag(iso):
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in iso)


def price_of(cc):
    row = db.execute("SELECT price FROM prices WHERE cc=?", (cc,)).fetchone()
    return row[0] if row else round(COUNTRIES[cc][1] * MARKUP, 2)


def fmt(p):
    return f"{p:g}"


def new_token():
    """7 أرقام عشوائية للعرض فقط"""
    return "".join(random.choices("0123456789", k=7))


def shown_number(cc, token):
    """مثال: +2130765..719"""
    return f"+{COUNTRIES[cc][0]}{token[:4]}..{token[4:]}"


# ---------- الواجهة ----------
def support_url():
    if CONTACT_TELEGRAM:
        return f"https://t.me/{CONTACT_TELEGRAM.lstrip('@')}"
    return f"tg://user?id={ADMIN}"


def support_markup(uid):
    return M([
        [B("Telegram", url=support_url()),
         B("Instagram", url=f"https://instagram.com/{CONTACT_INSTAGRAM.lstrip('@')}")],
        [B(tr(uid, "back"), callback_data="home")]])


LANG_PROMPT = f"<b>{BRAND}</b>\n{LINE}\nاختر لغتك  |  Choisissez votre langue  |  Choose your language"


def lang_markup():
    return M([[B(name, callback_data=f"lang:{code}")] for code, name in LANGS.items()])


def home_markup(uid):
    rows = []
    for i in range(0, len(APPS), 2):
        rows.append([B(a, callback_data=f"app:{APPS.index(a)}:0") for a in APPS[i:i + 2]])
    rows.append([B(tr(uid, "language"), callback_data="lang"),
                 B(tr(uid, "support_btn"), callback_data="support")])
    return M(rows)


def home_text(uid):
    return f"<b>{BRAND}</b>\n{LINE}\n{tr(uid, 'welcome')}"


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not get_lang(uid):
        await update.message.reply_text(LANG_PROMPT, parse_mode=HTML, reply_markup=lang_markup())
    else:
        await update.message.reply_text(home_text(uid), parse_mode=HTML, reply_markup=home_markup(uid))


def stock_of(app):
    return dict(db.execute(
        "SELECT cc, COUNT(*) FROM numbers WHERE app=? AND status='free' GROUP BY cc", (app,)))


async def show_countries(q, uid, app_i, page):
    """قائمة الدول: سطر واحد لكل دولة، تنزل للأسفل"""
    app = APPS[app_i]
    lang = get_lang(uid) or "en"
    stock = stock_of(app)
    avail = lambda c: ALWAYS_AVAILABLE or c in stock
    items = sorted(COUNTRIES, key=lambda c: (not avail(c), cname(c, lang)))
    pages = (len(items) - 1) // PER_PAGE + 1
    page = max(0, min(page, pages - 1))
    chunk = items[page * PER_PAGE:(page + 1) * PER_PAGE]
    tag = tr(uid, "soldout_tag")
    rows = []
    for cc in chunk:
        label = f"{flag(cc)}  {cname(cc, lang)}  +{COUNTRIES[cc][0]}  |  {fmt(price_of(cc))}$"
        if not avail(cc):
            label += f"  |  {tag}"
        rows.append([B(label, callback_data=f"cty:{app_i}:{cc}")])
    nav = []
    if page > 0:
        nav.append(B("‹", callback_data=f"app:{app_i}:{page - 1}"))
    nav.append(B(f"{page + 1} / {pages}", callback_data="noop"))
    if page < pages - 1:
        nav.append(B("›", callback_data=f"app:{app_i}:{page + 1}"))
    rows.append(nav)
    rows.append([B(tr(uid, "back"), callback_data="home")])
    await q.edit_message_text(f"<b>{app}</b>\n{LINE}\n{tr(uid, 'pick_country')}",
                              parse_mode=HTML, reply_markup=M(rows))


async def show_numbers(q, uid, app_i, cc):
    """أرقام معروضة (منقّطة في الوسط) للاختيار"""
    app = APPS[app_i]
    lang = get_lang(uid) or "en"
    if not ALWAYS_AVAILABLE and cc not in stock_of(app):
        await q.edit_message_text(
            tr(uid, "sold_out"),
            reply_markup=M([[B(tr(uid, "back"), callback_data=f"app:{app_i}:0")]]))
        return
    btns = []
    for _ in range(SHOWN_NUMBERS):
        t = new_token()
        btns.append(B(shown_number(cc, t), callback_data=f"buy:{app_i}:{cc}:{t}"))
    rows = [btns[i:i + 2] for i in range(0, len(btns), 2)]
    rows.append([B(tr(uid, "more_numbers"), callback_data=f"cty:{app_i}:{cc}")])
    rows.append([B(tr(uid, "back"), callback_data=f"app:{app_i}:0")])
    text = (f"<b>{app}  |  {flag(cc)} {cname(cc, lang)}  |  {fmt(price_of(cc))}$</b>\n{LINE}\n"
            f"{tr(uid, 'pick_number')}\n\n<i>{tr(uid, 'numbers_note')}</i>")
    await q.edit_message_text(text, parse_mode=HTML, reply_markup=M(rows))


def phone_of(order_id):
    o = db.execute("SELECT number_id, phone FROM orders WHERE id=?", (order_id,)).fetchone()
    if not o:
        return ""
    if o[0]:
        r = db.execute("SELECT phone FROM numbers WHERE id=?", (o[0],)).fetchone()
        return r[0] if r else ""
    return o[1] or ""


def release(order_id):
    o = db.execute("SELECT number_id FROM orders WHERE id=?", (order_id,)).fetchone()
    if o and o[0]:
        db.execute("UPDATE numbers SET status='free' WHERE id=? AND status='reserved'", (o[0],))
    db.commit()


async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data.split(":")
    uid = q.from_user.id
    act = d[0]

    if act == "noop":
        return

    if act == "lang":
        if len(d) == 1:
            await q.edit_message_text(LANG_PROMPT, parse_mode=HTML, reply_markup=lang_markup())
        else:
            set_lang(uid, d[1])
            await q.edit_message_text(home_text(uid), parse_mode=HTML, reply_markup=home_markup(uid))

    elif act == "home":
        await q.edit_message_text(home_text(uid), parse_mode=HTML, reply_markup=home_markup(uid))

    elif act == "support":
        await q.edit_message_text(tr(uid, "support_msg", email=escape(CONTACT_EMAIL)),
                                  parse_mode=HTML, reply_markup=support_markup(uid))

    elif act == "app":
        await show_countries(q, uid, int(d[1]), int(d[2]))

    elif act == "cty":
        await show_numbers(q, uid, int(d[1]), d[2])

    elif act == "buy":
        app_i, cc, token = int(d[1]), d[2], d[3]
        app = APPS[app_i]
        lang = get_lang(uid) or "en"
        n = db.execute("SELECT id FROM numbers WHERE app=? AND cc=? AND status='free' LIMIT 1",
                       (app, cc)).fetchone()
        if not n and not ALWAYS_AVAILABLE:
            await q.edit_message_text(
                tr(uid, "sold_out"),
                reply_markup=M([[B(tr(uid, "back"), callback_data=f"app:{app_i}:0")]]))
            return
        p = price_of(cc)
        nid = n[0] if n else None
        cur = db.execute(
            "INSERT INTO orders(user_id, username, app, cc, price, status, number_id) VALUES(?,?,?,?,?,?,?)",
            (uid, q.from_user.username or "", app, cc, p, "pending", nid))
        if nid:
            db.execute("UPDATE numbers SET status='reserved' WHERE id=?", (nid,))
        db.commit()
        oid = cur.lastrowid
        text = tr(uid, "order", oid=oid, app=app,
                  country=f"{flag(cc)} {cname(cc, lang)} (+{COUNTRIES[cc][0]})",
                  shown=shown_number(cc, token), amount=fmt(p),
                  network=escape(NETWORK), wallet=escape(WALLET))
        await q.edit_message_text(text, parse_mode=HTML, reply_markup=M([
            [B(tr(uid, "paid_btn"), callback_data=f"paid:{oid}")],
            [B(tr(uid, "cancel_btn"), callback_data=f"cancel:{oid}")],
            [B(tr(uid, "support_btn"), url=support_url())]]))

    elif act == "cancel":
        oid = int(d[1])
        o = db.execute("SELECT user_id, status FROM orders WHERE id=?", (oid,)).fetchone()
        if o and o[0] == uid and o[1] in ("pending", "review"):
            release(oid)
            db.execute("UPDATE orders SET status='cancelled' WHERE id=?", (oid,))
            db.commit()
            await q.edit_message_text(tr(uid, "cancelled"),
                                      reply_markup=M([[B(tr(uid, "home"), callback_data="home")]]))

    elif act == "paid":
        oid = int(d[1])
        o = db.execute("SELECT user_id, status FROM orders WHERE id=?", (oid,)).fetchone()
        if o and o[0] == uid and o[1] == "pending":
            ctx.user_data["proof"] = oid
            await q.message.reply_text(tr(uid, "send_proof"))

    elif act == "code":
        oid = int(d[1])
        o = db.execute("SELECT user_id, status, app, cc, number_id FROM orders WHERE id=?", (oid,)).fetchone()
        if not o or o[0] != uid or o[1] not in ("paid", "delivered"):
            return
        phone = phone_of(oid)
        await ctx.bot.send_message(
            ADMIN,
            f"الزبون ينتظر الكود\nطلب #{oid} | {o[2]} | {o[3]}\nالرقم: <code>{escape(phone)}</code>",
            parse_mode=HTML, reply_markup=M([[B("إرسال الكود", callback_data=f"send:{oid}")]]))
        await q.message.reply_text(tr(uid, "code_wait"))

    # ----- أزرار الأدمن -----
    elif uid == ADMIN and act == "ok":
        oid = int(d[1])
        o = db.execute("SELECT user_id, status, number_id FROM orders WHERE id=?", (oid,)).fetchone()
        if not o or o[1] not in ("review", "pending"):
            await q.edit_message_text("هذا الطلب تمت معالجته من قبل.")
            return
        if not o[2]:
            db.execute("UPDATE orders SET status='need_number' WHERE id=?", (oid,))
            db.commit()
            await q.edit_message_text(
                f"تم تأكيد دفع الطلب #{oid}. لا يوجد رقم في المخزون، أرسل الرقم الفعلي للزبون.",
                reply_markup=M([[B("إرسال الرقم", callback_data=f"num:{oid}")]]))
            return
        db.execute("UPDATE orders SET status='paid' WHERE id=?", (oid,))
        db.commit()
        phone = phone_of(oid)
        await ctx.bot.send_message(
            o[0], tr(o[0], "confirmed", phone=escape(phone)), parse_mode=HTML,
            reply_markup=M([[B(tr(o[0], "code_btn"), callback_data=f"code:{oid}")]]))
        await q.edit_message_text(f"تم تأكيد الطلب #{oid} وإرسال الرقم للزبون.")

    elif uid == ADMIN and act == "no":
        oid = int(d[1])
        o = db.execute("SELECT user_id, status FROM orders WHERE id=?", (oid,)).fetchone()
        if not o or o[1] not in ("review", "pending", "need_number"):
            await q.edit_message_text("هذا الطلب تمت معالجته من قبل.")
            return
        release(oid)
        db.execute("UPDATE orders SET status='rejected' WHERE id=?", (oid,))
        db.commit()
        await ctx.bot.send_message(
            o[0], tr(o[0], "rejected", oid=oid),
            reply_markup=M([[B(tr(o[0], "support_btn"), url=support_url())]]))
        await q.edit_message_text(f"تم رفض الطلب #{oid}.")

    elif uid == ADMIN and act == "num":
        ctx.user_data["numfor"] = int(d[1])
        await q.message.reply_text(f"أرسل الآن الرقم الفعلي للطلب #{d[1]} (مثال: +213551111111).")

    elif uid == ADMIN and act == "send":
        ctx.user_data["sending"] = int(d[1])
        await q.message.reply_text(f"أرسل الآن الكود للطلب #{d[1]} وسأحوّله للزبون مباشرة.")


# ---------- الرسائل ----------
async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = update.message
    uid = m.from_user.id

    # الأدمن يرسل الرقم الفعلي (عند عدم توفر مخزون)
    if uid == ADMIN and ctx.user_data.get("numfor") and m.text:
        oid = ctx.user_data.pop("numfor")
        o = db.execute("SELECT user_id FROM orders WHERE id=?", (oid,)).fetchone()
        if o:
            phone = m.text.strip()
            db.execute("UPDATE orders SET phone=?, status='paid' WHERE id=?", (phone, oid))
            db.commit()
            await ctx.bot.send_message(
                o[0], tr(o[0], "confirmed", phone=escape(phone)), parse_mode=HTML,
                reply_markup=M([[B(tr(o[0], "code_btn"), callback_data=f"code:{oid}")]]))
            await m.reply_text("تم إرسال الرقم للزبون.")
        return

    # الأدمن يرسل الكود
    if uid == ADMIN and ctx.user_data.get("sending") and m.text:
        oid = ctx.user_data.pop("sending")
        o = db.execute("SELECT user_id, number_id FROM orders WHERE id=?", (oid,)).fetchone()
        if o:
            await ctx.bot.send_message(
                o[0], tr(o[0], "code_msg", code=escape(m.text)), parse_mode=HTML,
                reply_markup=M([[B(tr(o[0], "code_again_btn"), callback_data=f"code:{oid}")],
                                [B(tr(o[0], "home"), callback_data="home")]]))
            db.execute("UPDATE orders SET status='delivered' WHERE id=?", (oid,))
            db.execute("UPDATE numbers SET status='sold' WHERE id=?", (o[1],))
            db.commit()
            await m.reply_text("تم إرسال الكود للزبون.")
        return

    # الزبون يرسل إثبات الدفع
    oid = ctx.user_data.get("proof")
    if oid:
        ctx.user_data.pop("proof")
        o = db.execute("SELECT app, cc, price, number_id FROM orders WHERE id=?", (oid,)).fetchone()
        stock_line = "المخزون: محجوز" if o[3] else "المخزون: غير متوفر، سترسل الرقم يدويا بعد التأكيد"
        db.execute("UPDATE orders SET status='review' WHERE id=?", (oid,))
        db.commit()
        u = m.from_user
        await ctx.bot.send_message(
            ADMIN,
            f"دفع جديد للمراجعة\nطلب #{oid} | {o[0]} | {o[1]} | {fmt(o[2])} USDT\n"
            f"{stock_line}\nالزبون: {escape(u.full_name)} @{u.username or '-'}",
            reply_markup=M([[B("تأكيد", callback_data=f"ok:{oid}"),
                             B("رفض", callback_data=f"no:{oid}")]]))
        await m.copy(chat_id=ADMIN)
        await m.reply_text(tr(uid, "proof_ok"))
        return

    await start(update, ctx)


# ---------- أوامر الأدمن ----------
def admin_only(fn):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN:
            return
        await fn(update, ctx)
    return wrapper


@admin_only
async def panel(update, ctx):
    await update.message.reply_text(
        "لوحة التحكم:\n\n"
        "/add التطبيق الدولة رقم1 رقم2 ...\n"
        "مثال: /add WhatsApp DZ +213551111111 +213552222222\n\n"
        "/stock عرض المخزون\n"
        "/setprice الدولة السعر\n"
        "مثال: /setprice DZ 0.8\n\n"
        f"التطبيقات المتاحة: {', '.join(APPS)}")


@admin_only
async def add(update, ctx):
    if len(ctx.args) < 3:
        await update.message.reply_text("الصيغة: /add WhatsApp DZ +213551111111")
        return
    app = next((a for a in APPS if a.lower() == ctx.args[0].lower()), None)
    cc = ctx.args[1].upper()
    if not app or cc not in COUNTRIES:
        await update.message.reply_text("اسم التطبيق أو رمز الدولة غير صحيح. اكتب /panel للمساعدة.")
        return
    for phone in ctx.args[2:]:
        db.execute("INSERT INTO numbers(app, cc, phone) VALUES(?,?,?)", (app, cc, phone))
    db.commit()
    await update.message.reply_text(
        f"تمت إضافة {len(ctx.args) - 2} رقم إلى {app} / {cc} ({cname(cc, 'ar')})")


@admin_only
async def stock(update, ctx):
    rows = db.execute(
        "SELECT app, cc, COUNT(*) FROM numbers WHERE status='free' GROUP BY app, cc ORDER BY app, cc").fetchall()
    if not rows:
        await update.message.reply_text("المخزون فارغ.")
        return
    await update.message.reply_text(
        "\n".join(f"{a} | {c} {cname(c, 'ar')}: {n}" for a, c, n in rows))


@admin_only
async def setprice(update, ctx):
    try:
        cc, p = ctx.args[0].upper(), float(ctx.args[1])
        assert cc in COUNTRIES
    except Exception:
        await update.message.reply_text("الصيغة: /setprice DZ 0.8")
        return
    db.execute("INSERT OR REPLACE INTO prices(cc, price) VALUES(?,?)", (cc, p))
    db.commit()
    await update.message.reply_text(f"سعر {cc} ({cname(cc, 'ar')}) أصبح {fmt(p)}$")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("panel", panel))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("setprice", setprice))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(~filters.COMMAND, on_message))
    app.run_polling()


if __name__ == "__main__":
    main()

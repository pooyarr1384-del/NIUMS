import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID

# ==========================================
# 1. کلاس‌های State
# ==========================================
class SupportState(StatesGroup):
    msg = State()

class AdminReplyState(StatesGroup):
    waiting_for_reply = State()

class AdminState(StatesGroup):
    waiting_for_new_text = State()
    waiting_for_file = State()

# ==========================================
# 2. دیتابیس
# ==========================================
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS menu_buttons (id INTEGER PRIMARY KEY, parent TEXT, text TEXT, callback TEXT, content TEXT, file_id TEXT, is_locked BOOLEAN DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS ratings (user_id INTEGER, callback TEXT, rating INTEGER, PRIMARY KEY (user_id, callback))')
    c.execute('CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)')
    c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
    except: pass
    finally: conn.close()

def get_total_users():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    return c.fetchone()[0]

def get_all_users():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def is_admin(user_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def add_admin(user_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    if user_id == ADMIN_ID: return
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_average_rating(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT AVG(rating) FROM ratings WHERE callback = ?', (callback,))
    res = c.fetchone()[0]
    conn.close()
    return round(res, 1) if res else "بدون امتیاز"

def save_rating(user_id, callback, rating):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO ratings (user_id, callback, rating) VALUES (?, ?, ?)', (user_id, callback, rating))
    conn.commit()
    conn.close()

def add_menu_button(parent, text, callback, content="اطلاعات در حال به‌روزرسانی.", file_id="", is_locked=False):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO menu_buttons (parent, text, callback, content, file_id, is_locked) VALUES (?, ?, ?, ?, ?, ?)', (parent, text, callback, content, file_id, is_locked))
    conn.commit()
    conn.close()

def get_buttons(parent):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT text, callback, content, file_id, is_locked FROM menu_buttons WHERE parent = ?', (parent,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_button_content(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT content, file_id, is_locked FROM menu_buttons WHERE callback = ?', (callback,))
    row = c.fetchone()
    conn.close()
    return row if row else ("اطلاعات در دسترس نیست", "", 0)

def update_button_text(callback, new_text):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE menu_buttons SET content = ? WHERE callback = ?', (new_text, callback))
    conn.commit()
    conn.close()

def update_button_file(callback, file_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE menu_buttons SET file_id = ? WHERE callback = ?', (file_id, callback))
    conn.commit()
    conn.close()

def update_button_lock(callback, is_locked):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE menu_buttons SET is_locked = ? WHERE callback = ?', (is_locked, callback))
    conn.commit()
    conn.close()

def delete_button(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM menu_buttons WHERE callback = ?', (callback,))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 3. تنظیم دکمه‌های اولیه
# ==========================================
def init_default_buttons():
    if not get_buttons("main"):
        add_menu_button("main", "🫀 داخلی - جراحی", "sub_internal")
        add_menu_button("main", "🍼 کودکان", "sub_pediatric")
        add_menu_button("main", "👴 سالمندان", "sub_geriatric")
        add_menu_button("main", "🤱 مادر و نوزاد", "sub_obstetric")
        add_menu_button("main", "🧠 روان پرستاری", "sub_psychiatry")
        add_menu_button("main", "🌿 پرستاری سلامت", "sub_health")
        add_menu_button("main", "🩺 پرستاری بهداشت", "sub_hygiene")
        add_menu_button("main", "💉 مراقبت‌های ویژه", "sub_icu")
        add_menu_button("main", "🚑 فوریت‌های پزشکی", "sub_emergency")
        add_menu_button("main", "📋 فرایندهای پرستاری", "sub_process")
        add_menu_button("main", "📚 رفرنس‌های پرستاری", "sub_references")
        add_menu_button("main", "🧬 علوم پایه", "sub_basic_science")
        add_menu_button("main", "📖 دروس عمومی/زبان", "sub_general")
        add_menu_button("main", "🏥 پراتیک و کارآموزی", "sub_practice")
        add_menu_button("main", "📞 پشتیبانی", "contact_instructor")
        add_menu_button("main", "👑 VIP", "sub_vip")
        add_menu_button("main", "🏥 درباره ما", "about_us")
        add_menu_button("main", "🧰 ابزارهای پرستاری", "tools_menu")

        # زیرمنوی ابزارها
        add_menu_button("tools_menu", "🧮 ماشین حساب BMI", "tool_bmi")
        add_menu_button("tools_menu", "💊 دوز دارو", "tool_drug")
        add_menu_button("tools_menu", "💧 مایعات وریدی", "tool_fluids")
        add_menu_button("tools_menu", "🩸 قطره‌چکان (IV Drip)", "tool_drip")
        add_menu_button("tools_menu", "📏 تبدیل واحدها", "tool_convert")
        add_menu_button("tools_menu", "💊 جدول داروها", "tool_drugs")
        add_menu_button("tools_menu", "📋 راهنمای مهارت‌ها", "tool_skills")

        add_menu_button("sub_health", "👤 فرد", "health_ind")
        add_menu_button("sub_health", "🏠 محیط", "health_env")
        add_menu_button("sub_health", "🌍 جامعه", "health_soc")

        add_menu_button("sub_general", "🧠 روان عمومی", "gen_psych")
        add_menu_button("sub_general", "🗣️ زبان تخصصی", "gen_lang")
        add_menu_button("sub_general", "📖 معارف", "gen_rel")
        add_menu_button("sub_general", "✍️ ادبیات", "gen_lit")
        add_menu_button("sub_general", "🏃 تربیت بدنی", "gen_pe")

        add_menu_button("sub_basic_science", "🥗 تغذیه", "bas_nut")
        add_menu_button("sub_basic_science", "💊 فارماکولوژی", "bas_phar")
        add_menu_button("sub_basic_science", "🔬 انگل‌شناسی", "bas_par")
        add_menu_button("sub_basic_science", "❤️ فیزیولوژی", "bas_phy")
        add_menu_button("sub_basic_science", "🦴 آناتومی", "bas_ana")
        add_menu_button("sub_basic_science", "🧪 بیوشیمی", "bas_bio")
        add_menu_button("sub_basic_science", "📈 اپیدمیولوژی", "bas_epi")
        add_menu_button("sub_basic_science", "🛡️ ایمنولوژی", "bas_imm")
        add_menu_button("sub_basic_science", "🦠 میکروب‌شناسی", "bas_mic")

        add_menu_button("sub_practice", "🩺 پراتیک", "pra_cli")
        add_menu_button("sub_practice", "🏥 کارآموزی", "pra_int")

        add_menu_button("sub_vip", "👨‍🏫 تدریس", "vip_teach")
        add_menu_button("sub_vip", "📂 جزوات ویژه", "vip_files")
        add_menu_button("sub_vip", "📝 آزمون ویژه", "vip_quiz")

init_default_buttons()

# ==========================================
# 4. ساخت کیبورد
# ==========================================
def build_keyboard(parent, show_back=True):
    buttons = get_buttons(parent)
    keyboard = []
    row = []
    for i, btn in enumerate(buttons):
        text = btn[0]
        callback = btn[1]
        is_locked = btn[4]
        display_text = f"🔒 {text}" if is_locked else text
        row.append(InlineKeyboardButton(text=display_text, callback_data=callback))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    if show_back:
        keyboard.append([InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def check_membership(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])

# ==========================================
# 5. روت‌های اصلی کاربران
# ==========================================
main_router = Router()

@main_router.message(Command("start"))
async def start_cmd(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    
    caption_text = (
        f"🌸 *سلام {message.from_user.first_name} عزیز!*\n\n"
        "👩‍⚕️ به *آکادمی پرستاری* خوش آمدید!\n"
        "ارائه بهترین محتویات آموزشی ویژه دانشجویان پرستاری\n"
        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "🏛️ *دانشگاه علوم پزشکی ایران*\n"
        "پیشگام در آموزش نوین\n"
        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "👇 *برای شروع، یکی از بخش‌های زیر را انتخاب کنید:*"
    )
    
    await message.answer_photo(
        photo="https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?q=80&w=1000&auto=format&fit=crop",
        caption=caption_text,
        reply_markup=build_keyboard("main"),
        parse_mode="Markdown"
    )

@main_router.callback_query(F.data == "back_to_main")
async def go_back(callback: CallbackQuery):
    await callback.message.answer("✨ منوی اصلی:", reply_markup=build_keyboard("main"), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith(("sub_", "health_", "gen_", "bas_", "pra_", "vip_")))
async def handle_dynamic_buttons(callback: CallbackQuery):
    data = callback.data
    
    if data in ["sub_health", "sub_general", "sub_basic_science", "sub_practice", "sub_vip", "tools_menu"]:
        await callback.message.answer("📂 منوی مربوطه:", reply_markup=build_keyboard(data), parse_mode="Markdown")
        await callback.answer()
        return
    
    content, file_id, is_locked = get_button_content(data)
    
    if is_locked:
        is_member = await check_membership(callback.bot, callback.from_user.id)
        if not is_member:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_ID}")],
                [InlineKeyboardButton(text="🔄 بررسی عضویت", callback_data=f"check_{data}")]
            ])
            await callback.message.answer(
                "🔒 *این محتوا قفل است!*\n\nبرای دسترسی به این بخش، لطفاً ابتدا در کانال ما عضو شوید.",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            await callback.answer()
            return
    
    if file_id:
        await callback.message.answer_document(document=file_id, caption=content, parse_mode="Markdown")
    else:
        await callback.message.answer(content, parse_mode="Markdown")
    await callback.answer()

# ==========================================
# 6. هندلرهای اختصاصی ابزارها
# ==========================================
@main_router.callback_query(F.data == "tool_bmi")
async def tool_bmi(callback: CallbackQuery):
    await callback.message.answer(
        "🧮 *محاسبه BMI*\n\n"
        "لطفاً وزن (کیلوگرم) و قد (متر) را با فاصله بفرستید.\n"
        "مثال: `75 1.75`\n\n"
        "⚠️ اگر قد را به سانتی‌متر می‌فرستید، عدد بزرگتر از ۳ را بفرستید (مثلاً ۱۷۵).",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_drug")
async def tool_drug(callback: CallbackQuery):
    await callback.message.answer(
        "💊 *محاسبه دوز دارو*\n\n"
        "۳ عدد را با فاصله بفرستید:\n"
        "۱. دوز تجویزی (mg/kg)\n"
        "۲. وزن بیمار (kg)\n"
        "۳. غلظت ویال (mg/ml)\n\n"
        "مثال: `5 70 10`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_fluids")
async def tool_fluids(callback: CallbackQuery):
    await callback.message.answer(
        "💧 *محاسبه مایعات وریدی*\n\n"
        "وزن بیمار (کیلوگرم) را بفرستید.\n"
        "مثال: `70`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_drip")
async def tool_drip(callback: CallbackQuery):
    await callback.message.answer(
        "🩸 *محاسبه قطره‌چکان (IV Drip)*\n\n"
        "۳ عدد را با فاصله بفرستید:\n"
        "۱. حجم سرم (ml)\n"
        "۲. فاکتور قطره (معمولاً ۱۰، ۱۵ یا ۲۰)\n"
        "۳. زمان (ساعت)\n\n"
        "مثال: `1000 20 8`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_convert")
async def tool_convert(callback: CallbackQuery):
    await callback.message.answer(
        "📏 *تبدیل واحدها*\n\n"
        "یکی از فرمت‌های زیر را بفرستید:\n"
        "🔹 میلی‌گرم به میکروگرم: `mg mcg [مقدار]`\n"
        "🔹 سانتی‌گراد به فارنهایت: `c f [مقدار]`\n"
        "🔹 میلی‌لیتر به قطره: `ml drop [مقدار]`\n\n"
        "مثال: `mg mcg 500`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_drugs")
async def tool_drugs(callback: CallbackQuery):
    await callback.message.answer(
        "💊 *جدول داروها*\n\n"
        "نام دارو را بفرستید تا اطلاعات آن را ببینید.\n"
        "مثال: `اپی‌نفرین`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "tool_skills")
async def tool_skills(callback: CallbackQuery):
    await callback.message.answer(
        "📋 *راهنمای مهارت‌ها*\n\n"
        "نام مهارت را بفرستید.\n"
        "مثال: `پانسمان`",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ==========================================
# 7. پردازشگرهای ورودی ابزارها
# ==========================================
@main_router.message(F.text.regexp(r'^\d+(\.\d+)?(\s+\d+(\.\d+)?)*$'))
async def handle_calc_input(message: Message):
    numbers = list(map(float, message.text.strip().split()))
    text = message.text.strip().lower()
    
    try:
        if len(numbers) == 1:
            weight = numbers[0]
            if weight <= 10: fluid = weight * 100
            elif weight <= 20: fluid = 1000 + (weight - 10) * 50
            else: fluid = 1500 + (weight - 20) * 20
            await message.answer(
                f"💧 *نتیجه مایعات*\n\n"
                f"وزن بیمار: {weight} kg\n"
                f"مایعات روزانه: **{fluid} ml**",
                parse_mode="Markdown"
            )
        
        elif len(numbers) == 3:
            vol, factor, hours = numbers[0], numbers[1], numbers[2]
            if factor in [10, 15, 20] and hours > 0:
                drops_per_min = (vol * factor) / (hours * 60)
                await message.answer(
                    f"🩸 *نتیجه قطره‌چکان*\n\n"
                    f"حجم: {vol} ml | فاکتور: {factor} | زمان: {hours}h\n"
                    f"قطره در دقیقه: **{drops_per_min:.0f} gtt/min**",
                    parse_mode="Markdown"
                )
            else:
                dose, weight, conc = numbers[0], numbers[1], numbers[2]
                total_dose = dose * weight
                vol_ml = total_dose / conc
                await message.answer(
                    f"💊 *نتیجه دوز دارو*\n\n"
                    f"دوز تجویزی: {dose} mg/kg\n"
                    f"وزن بیمار: {weight} kg\n"
                    f"غلظت ویال: {conc} mg/ml\n"
                    f"دوز کل: **{total_dose} mg**\n"
                    f"حجم از ویال: **{vol_ml:.2f} ml**",
                    parse_mode="Markdown"
                )
    except:
        await message.answer("❌ محاسبه با خطا مواجه شد. لطفاً اعداد را بررسی کنید.")

@main_router.message(F.text)
async def handle_text_inputs(message: Message):
    text = message.text.strip().lower()
    
    parts = text.split()
    if len(parts) == 3 and parts[0] in ["mg", "c", "ml"]:
        unit1, unit2, val = parts[0], parts[1], float(parts[2])
        if unit1 == "mg" and unit2 == "mcg":
            await message.answer(f"📏 **{val} mg** = **{val * 1000} mcg**")
        elif unit1 == "c" and unit2 == "f":
            await message.answer(f"📏 **{val}°C** = **{val * 1.8 + 32:.1f}°F**")
        elif unit1 == "ml" and unit2 == "drop":
            await message.answer(f"📏 **{val} ml** = **{val * 20} drops**")
        return
    
    try:
        with open("drugs.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    name, desc = line.split(":", 1)
                    if name.strip().lower() == text:
                        await message.answer(
                            f"💊 *{name.strip()}*\n\n{desc.strip()}",
                            parse_mode="Markdown"
                        )
                        return
    except: pass
    
    try:
        with open("skills.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    name, desc = line.split(":", 1)
                    if name.strip().lower() == text:
                        await message.answer(
                            f"📋 *{name.strip()}*\n\n{desc.strip()}",
                            parse_mode="Markdown"
                        )
                        return
    except: pass
    
    await message.answer("❌ موردی با این نام پیدا نشد. لطفاً از لیست ابزارها یا داروها استفاده کنید.")

# ==========================================
# 8. پنل ادمین
# ==========================================
SUB_MENUS = {
    "main": "منوی اصلی",
    "sub_health": "زیرمنوی پرستاری سلامت",
    "sub_general": "زیرمنوی دروس عمومی/زبان",
    "sub_basic_science": "زیرمنوی علوم پایه",
    "sub_practice": "زیرمنوی پراتیک و کارآموزی",
    "sub_vip": "زیرمنوی VIP",
    "tools_menu": "زیرمنوی ابزارهای پرستاری"
}

def build_admin_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📝 ویرایش منو و دکمه‌ها", callback_data="admin_edit_menu")],
        [InlineKeyboardButton(text="📎 مدیریت فایل‌های دکمه‌ها", callback_data="admin_files")],
        [InlineKeyboardButton(text="🔒 مدیریت قفل محتوا", callback_data="admin_locks")],
        [InlineKeyboardButton(text="📢 ارسال اطلاعیه به همه", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="👑 مدیریت ادمین‌ها (افزودن/حذف)", callback_data="admin_manage")],
        [InlineKeyboardButton(text="💬 پشتیبانی و پاسخ به کاربران", callback_data="admin_support")]
    ])

def build_admin_submenu_keyboard():
    keyboard = []
    for key, title in SUB_MENUS.items():
        keyboard.append([InlineKeyboardButton(text=f"📂 {title}", callback_data=f"adm_menu_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@main_router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ شما دسترسی به پنل مدیریت ندارید!")
        return
    await message.answer(
        "👑 *پنل مدیریت حرفه‌ای*\n\nبه بخش مدیریت ربات خود خوش آمدید. یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=build_admin_main_keyboard(),
        parse_mode="Markdown"
    )

@main_router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    total = get_total_users()
    await callback.message.answer(f"📊 *آمار ربات*\n\n👥 تعداد کل کاربران: *{total}* نفر", parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "admin_edit_menu")
async def admin_edit_menu_start(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("📂 *کدام منو را می‌خواهید ویرایش کنید؟*", reply_markup=build_admin_submenu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("adm_menu_"))
async def admin_edit_select_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    parent = callback.data.replace("adm_menu_", "")
    buttons = get_buttons(parent)
    if not buttons:
        await callback.message.answer("❌ این منو خالی است!")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn[0], callback_data=f"edit_{btn[1]}")] for btn in buttons
    ])
    await callback.message.answer(f"📝 *دکمه‌های منوی `{SUB_MENUS.get(parent, parent)}`:*\n\nکدام دکمه را می‌خواهید ویرایش کنید؟", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("edit_"))
async def admin_edit_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    callback_data = callback.data.replace("edit_", "")
    await state.set_state(AdminState.waiting_for_new_text)
    await state.update_data(target_callback=callback_data)
    await callback.message.answer(f"📝 کد دکمه `{callback_data}` انتخاب شد.\n\n👉 حالا *متن جدید* را بفرستید:")
    await callback.answer()

@main_router.message(AdminState.waiting_for_new_text)
async def admin_save_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    update_button_text(data['target_callback'], message.text)
    await state.clear()
    await message.answer("✅ متن با موفقیت تغییر کرد!")

@main_router.callback_query(F.data == "admin_files")
async def admin_files_start(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("📂 *برای کدام منو می‌خواهید فایل آپلود کنید؟*", reply_markup=build_admin_submenu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("adm_menu_"))
async def admin_file_select_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    parent = callback.data.replace("adm_menu_", "")
    buttons = get_buttons(parent)
    if not buttons:
        await callback.message.answer("❌ این منو خالی است!")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn[0], callback_data=f"upload_{btn[1]}")] for btn in buttons
    ])
    await callback.message.answer(f"📎 *دکمه‌های منوی `{SUB_MENUS.get(parent, parent)}`:*\n\nبرای کدام دکمه فایل می‌خواهید؟", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("upload_"))
async def admin_upload_selected(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    callback_data = callback.data.replace("upload_", "")
    await state.set_state(AdminState.waiting_for_file)
    await state.update_data(target_callback=callback_data)
    await callback.message.answer(f"📎 کد دکمه `{callback_data}` انتخاب شد.\n\n👉 حالا فایل (PDF) را بفرستید:")
    await callback.answer()

@main_router.message(AdminState.waiting_for_file)
async def admin_save_file(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    if not message.document:
        await message.answer("❌ لطفاً یک فایل بفرستید.")
        return
    data = await state.get_data()
    update_button_file(data['target_callback'], message.document.file_id)
    await state.clear()
    await message.answer("✅ فایل با موفقیت آپلود شد!")

@main_router.callback_query(F.data == "admin_locks")
async def admin_locks_start(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("🔒 *کدام منو را می‌خواهید قفل/باز کنید؟*", reply_markup=build_admin_submenu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("adm_menu_"))
async def admin_lock_select_menu(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    parent = callback.data.replace("adm_menu_", "")
    buttons = get_buttons(parent)
    if not buttons:
        await callback.message.answer("❌ این منو خالی است!")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'🔒' if btn[4] else '🔓'} {btn[0]}", callback_data=f"toggle_{btn[1]}")] for btn in buttons
    ])
    await callback.message.answer(f"🔒 *دکمه‌های منوی `{SUB_MENUS.get(parent, parent)}`:*\n\nبرای تغییر وضعیت قفل روی هر دکمه کلیک کنید:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith("toggle_"))
async def admin_toggle_lock(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    callback_data = callback.data.replace("toggle_", "")
    content, _, current_lock = get_button_content(callback_data)
    new_lock = 0 if current_lock else 1
    update_button_lock(callback_data, new_lock)
    status = "قفل شد" if new_lock else "باز شد"
    await callback.message.answer(f"✅ قفل دکمه `{callback_data}` با موفقیت {status}!", reply_markup=back_btn())
    await callback.answer()

@main_router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("📢 *ارسال اطلاعیه*\n\nلطفاً متن اطلاعیه را بفرستید. اگر همراه با عکس/فایل است، آن را با کپشن بفرستید.\n\nبرای لغو: /cancel")
    await state.set_state(AdminState.waiting_for_new_text)
    await callback.answer()

@main_router.message(AdminState.waiting_for_new_text)
async def admin_send_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    users = get_all_users()
    count = 0
    failed = 0
    await message.answer(f"🔄 در حال ارسال به {len(users)} کاربر...")
    for user_id in users:
        try:
            if message.text:
                await message.bot.send_message(user_id, message.text, parse_mode="Markdown")
            elif message.caption and (message.photo or message.document or message.video):
                if message.photo:
                    await message.bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption, parse_mode="Markdown")
                elif message.document:
                    await message.bot.send_document(user_id, message.document.file_id, caption=message.caption, parse_mode="Markdown")
                elif message.video:
                    await message.bot.send_video(user_id, message.video.file_id, caption=message.caption, parse_mode="Markdown")
            count += 1
        except:
            failed += 1
    await state.clear()
    await message.answer(f"✅ ارسال کامل شد!\nموفق: {count}\nناموفق: {failed}")

@main_router.callback_query(F.data == "admin_manage")
async def admin_manage_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن ادمین جدید", callback_data="admin_add")],
        [InlineKeyboardButton(text="➖ حذف ادمین", callback_data="admin_remove")]
    ])
    await callback.message.answer("👑 *مدیریت ادمین‌ها*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data == "admin_add")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("➕ *افزودن ادمین جدید*\n\nلطفاً آیدی عددی کاربر مورد نظر را بفرستید:", reply_markup=back_btn())
    await state.set_state(AdminState.waiting_for_new_text)
    await state.update_data(action="add_admin")
    await callback.answer()

@main_router.callback_query(F.data == "admin_remove")
async def admin_remove_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("➖ *حذف ادمین*\n\nلطفاً آیدی عددی کاربر مورد نظر را بفرستید. (نکته: ادمین اصلی قابل حذف نیست)", reply_markup=back_btn())
    await state.set_state(AdminState.waiting_for_new_text)
    await state.update_data(action="remove_admin")
    await callback.answer()

@main_router.message(AdminState.waiting_for_new_text)
async def admin_manage_process(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    data = await state.get_data()
    action = data.get("action")
    try:
        target_id = int(message.text.strip())
        if action == "add_admin":
            if is_admin(target_id):
                await message.answer("⚠️ این کاربر هم‌اکنون ادمین است.")
            else:
                add_admin(target_id)
                await message.answer(f"✅ کاربر با آیدی `{target_id}` با موفقیت به لیست ادمین‌ها اضافه شد!")
        elif action == "remove_admin":
            if target_id == ADMIN_ID:
                await message.answer("⛔ شما نمی‌توانید ادمین اصلی را حذف کنید!")
            elif not is_admin(target_id):
                await message.answer("⚠️ این کاربر ادمین نیست.")
            else:
                remove_admin(target_id)
                await message.answer(f"✅ کاربر با آیدی `{target_id}` از لیست ادمین‌ها حذف شد!")
    except ValueError:
        await message.answer("❌ لطفاً یک آیدی عددی معتبر بفرستید.")
    await state.clear()

@main_router.callback_query(F.data == "admin_support")
async def admin_support_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    await callback.message.answer("💬 *بخش پشتیبانی*\n\nوقتی کاربری به شما پیام می‌دهد، زیر پیام او در این ربات یک دکمه `پاسخ` ظاهر می‌شود. با کلیک روی آن می‌توانید پاسخ دهید.", parse_mode="Markdown")
    await callback.answer()

# ==========================================
# 9. اجرا
# ==========================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(main_router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
import os
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID

# ==========================================
# تشخیص محیط اجرا
# ==========================================
IS_LOCAL = os.environ.get("RAILWAY_ENVIRONMENT") is None

if IS_LOCAL:
    print("⚠️ هشدار: ربات روی کامپیوتر شخصی اجرا شد. متوقف شد تا تداخل پیش نیاید.")
    sys.exit()

# ==========================================
# دیتابیس
# ==========================================
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS menu_buttons 
                 (id INTEGER PRIMARY KEY, parent TEXT, text TEXT, callback TEXT, content TEXT, file_id TEXT, is_locked INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ratings 
                 (user_id INTEGER, callback TEXT, rating INTEGER, PRIMARY KEY (user_id, callback))''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?,?,?,?)', 
                  (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
    except: pass
    finally: conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def save_rating(user_id, callback, rating):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO ratings (user_id, callback, rating) VALUES (?,?,?)', (user_id, callback, rating))
    conn.commit()
    conn.close()

def add_menu_button(parent, text, callback, content="اطلاعات در حال به‌روزرسانی.", file_id="", is_locked=False):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO menu_buttons (parent, text, callback, content, file_id, is_locked) VALUES (?,?,?,?,?,?)', 
              (parent, text, callback, content, file_id, 1 if is_locked else 0))
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
    c.execute('UPDATE menu_buttons SET is_locked = ? WHERE callback = ?', (1 if is_locked else 0, callback))
    conn.commit()
    conn.close()

def build_keyboard(parent):
    buttons = get_buttons(parent)
    keyboard = []
    row = []
    for btn in buttons:
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
    keyboard.append([InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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
        add_menu_button("main", "🎓 آزمون‌ها", "quizzes")
        add_menu_button("main", "📞 پشتیبانی", "contact_instructor")
        add_menu_button("main", "👑 VIP", "sub_vip")
        add_menu_button("main", "🏥 درباره ما", "about_us")
        add_menu_button("main", "🧰 جعبه ابزار پرستاری", "toolbox")

        add_menu_button("toolbox", "🧮 ماشین حساب", "tool_calc")
        add_menu_button("toolbox", "📏 تبدیل واحدها", "tool_convert")
        add_menu_button("toolbox", "💧 مایعات وریدی", "tool_fluid")
        add_menu_button("toolbox", "🩸 قطره‌چکان (IV Drip)", "tool_drip")
        add_menu_button("toolbox", "💊 جدول مرجع داروها", "tool_drugs")
        add_menu_button("toolbox", "📋 راهنمای مهارت‌ها", "tool_skills")

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
        add_menu_button("quizzes", "📝 آزمون اصول و فنون", "quiz_fundamentals")

init_default_buttons()

# ==========================================
# روت‌ها
# ==========================================
router = Router()

class AdminState(StatesGroup):
    waiting_for_new_text = State()
    waiting_for_file = State()

class AdminReplyState(StatesGroup):
    waiting_for_reply = State()

@router.message(Command("start"))
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

@router.callback_query(F.data == "back_to_main")
async def go_back(callback: CallbackQuery):
    await callback.message.answer("✨ منوی اصلی:", reply_markup=build_keyboard("main"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "toolbox")
async def open_toolbox(callback: CallbackQuery):
    await callback.message.answer("🧰 *جعبه ابزار پرستاری*\n\nیکی از ابزارهای زیر را انتخاب کنید:", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_calc")
async def tool_calculator(callback: CallbackQuery):
    calc_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 محاسبه BMI", callback_data="calc_bmi"),
         InlineKeyboardButton(text="💊 دوز دارو", callback_data="calc_drug")],
        [InlineKeyboardButton(text="🔙 بازگشت به جعبه ابزار", callback_data="toolbox")]
    ])
    await callback.message.answer("🧮 *ماشین حساب*\n\nیکی را انتخاب کنید:", reply_markup=calc_keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_convert")
async def tool_converter(callback: CallbackQuery):
    await callback.message.answer("📏 *تبدیل واحدها*\n\nفرمت ارسال:\n`mg mcg [عدد]`\n`c f [عدد]`\n`ml drop [عدد]`", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_fluid")
async def tool_fluid(callback: CallbackQuery):
    await callback.message.answer("💧 *مایعات وریدی*\n\nوزن بیمار (کیلوگرم) را بفرستید.", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_drip")
async def tool_drip(callback: CallbackQuery):
    await callback.message.answer("🩸 *قطره‌چکان (IV Drip)*\n\n۳ عدد بفرستید:\n`حجم` `فاکتور قطره` `زمان`", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_drugs")
async def tool_drugs(callback: CallbackQuery):
    await callback.message.answer("💊 *جدول داروها*\n\nنام دارو را بفرستید.", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "tool_skills")
async def tool_skills(callback: CallbackQuery):
    await callback.message.answer("📋 *راهنمای مهارت‌ها*\n\nنام مهارت را بفرستید.", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "calc_bmi")
async def calc_bmi(callback: CallbackQuery):
    await callback.message.answer("📝 وزن و قد را با فاصله بفرستید (مثال: ۷۵ ۱.۷۵)", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "calc_drug")
async def calc_drug(callback: CallbackQuery):
    await callback.message.answer("💊 ۳ عدد بفرستید: دوز(mg/kg) وزن(kg) غلظت(mg/ml)", reply_markup=build_keyboard("toolbox"), parse_mode="Markdown")
    await callback.answer()

@router.message(F.text)
async def handle_input(message: Message):
    text = message.text.strip()
    parts = text.split()
    
    # BMI
    if len(parts) == 2 and all(p.replace('.','',1).isdigit() for p in parts):
        w, h = float(parts[0]), float(parts[1])
        if h > 3: h /= 100
        bmi = w / (h*h)
        cat = "لاغر" if bmi < 18.5 else "نرمال" if bmi < 25 else "اضافه وزن" if bmi < 30 else "چاق"
        await message.answer(f"🧮 BMI: *{bmi:.1f}* ({cat})", parse_mode="Markdown")
    
    # Drug dose
    elif len(parts) == 3 and all(p.replace('.','',1).isdigit() for p in parts):
        dose, weight, conc = map(float, parts)
        total = dose * weight
        vol = total / conc
        await message.answer(f"💊 دوز کل: *{total} mg*\nحجم: *{vol:.2f} ml*", parse_mode="Markdown")
    
    # Conversions
    elif len(parts) == 3 and parts[0].lower() in ["mg", "c", "ml"]:
        unit1, unit2, val = parts[0].lower(), parts[1].lower(), float(parts[2])
        if unit1 == "mg" and unit2 == "mcg":
            await message.answer(f"📏 {val} mg = *{val*1000} mcg*")
        elif unit1 == "c" and unit2 == "f":
            await message.answer(f"📏 {val}°C = *{val*1.8+32:.1f}°F*")
        elif unit1 == "ml" and unit2 == "drop":
            await message.answer(f"📏 {val} ml = *{val*20} drops*")
    
    # IV Drip
    elif len(parts) == 3 and all(p.replace('.','',1).isdigit() for p in parts):
        vol, factor, hours = map(float, parts)
        rate = (vol * factor) / (hours * 60)
        await message.answer(f"🩸 قطره در دقیقه: *{rate:.0f} gtt/min*", parse_mode="Markdown")
    
    # IV Fluids
    elif len(parts) == 1 and parts[0].replace('.','',1).isdigit():
        w = float(parts[0])
        if w <= 10: fluid = w * 100
        elif w <= 20: fluid = 1000 + (w-10)*50
        else: fluid = 1500 + (w-20)*20
        await message.answer(f"💧 مایعات روزانه: *{fluid} ml*", parse_mode="Markdown")
    
    # Drug search
    else:
        try:
            with open("drugs.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        name, desc = line.split(":", 1)
                        if name.strip() == text:
                            await message.answer(f"💊 *{name.strip()}*\n{desc.strip()}", parse_mode="Markdown")
                            return
            with open("skills.txt", "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        name, desc = line.split(":", 1)
                        if name.strip() == text:
                            await message.answer(f"📋 *{name.strip()}*\n{desc.strip()}", parse_mode="Markdown")
                            return
            await message.answer("❌ چیزی پیدا نشد.", reply_markup=build_keyboard("toolbox"))
        except FileNotFoundError:
            await message.answer("❌ فایل‌های اطلاعاتی یافت نشد.")

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer(
        "👑 پنل ادمین:\nاز دکمه‌های زیر استفاده کنید:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 ویرایش متن", callback_data="admin_edit")],
            [InlineKeyboardButton(text="📎 آپلود فایل", callback_data="admin_file")]
        ])
    )

@router.callback_query(F.data == "admin_edit")
async def admin_edit(callback: CallbackQuery):
    await callback.message.answer("کد دکمه را بفرستید (مثلاً sub_internal).", reply_markup=build_keyboard("main"))
    await callback.answer()

@router.callback_query(F.data == "admin_file")
async def admin_file(callback: CallbackQuery):
    await callback.message.answer("کد دکمه را بفرستید و سپس فایل را آپلود کنید.", reply_markup=build_keyboard("main"))
    await callback.answer()

# ==========================================
# اجرا
# ==========================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

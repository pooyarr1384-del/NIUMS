import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID

# === دیتابیس ===
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS files (file_name TEXT UNIQUE, file_id TEXT)')
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

def save_file(file_name, file_id):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO files (file_name, file_id) VALUES (?, ?)', (file_name, file_id))
    conn.commit()
    conn.close()

def get_file_id(file_name):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT file_id FROM files WHERE file_name = ?', (file_name,))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

init_db()

# === کیبوردها ===
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌿 پرستاری سلامت", callback_data="sub_health")],
        [InlineKeyboardButton(text="📖 دروس عمومی/زبان", callback_data="sub_general")],
        [InlineKeyboardButton(text="🧬 علوم پایه", callback_data="sub_basic")],
        [InlineKeyboardButton(text="🏥 پراتیک و کارآموزی", callback_data="sub_practice")],
        [InlineKeyboardButton(text="👑 VIP", callback_data="sub_vip")],
        [InlineKeyboardButton(text="📞 ارتباط با ادمین", callback_data="contact_instructor")],
    ])

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

def health_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 فرد", callback_data="health_ind")],
        [InlineKeyboardButton(text="🏠 محیط", callback_data="health_env")],
        [InlineKeyboardButton(text="🌍 جامعه", callback_data="health_soc")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

def general_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 روان عمومی", callback_data="gen_psych")],
        [InlineKeyboardButton(text="🗣️ زبان تخصصی", callback_data="gen_lang")],
        [InlineKeyboardButton(text="📖 معارف", callback_data="gen_rel")],
        [InlineKeyboardButton(text="✍️ ادبیات", callback_data="gen_lit")],
        [InlineKeyboardButton(text="🏃 تربیت بدنی", callback_data="gen_pe")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

def basic_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🥗 تغذیه", callback_data="bas_nut")],
        [InlineKeyboardButton(text="💊 فارماکولوژی", callback_data="bas_phar")],
        [InlineKeyboardButton(text="🔬 انگل‌شناسی", callback_data="bas_par")],
        [InlineKeyboardButton(text="❤️ فیزیولوژی", callback_data="bas_phy")],
        [InlineKeyboardButton(text="🦴 آناتومی", callback_data="bas_ana")],
        [InlineKeyboardButton(text="🧪 بیوشیمی", callback_data="bas_bio")],
        [InlineKeyboardButton(text="📈 اپیدمیولوژی", callback_data="bas_epi")],
        [InlineKeyboardButton(text="🛡️ ایمنولوژی", callback_data="bas_imm")],
        [InlineKeyboardButton(text="🦠 میکروب‌شناسی", callback_data="bas_mic")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

def practice_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🩺 پراتیک", callback_data="pra_cli")],
        [InlineKeyboardButton(text="🏥 کارآموزی", callback_data="pra_int")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

def vip_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫 تدریس", callback_data="vip_teach")],
        [InlineKeyboardButton(text="📂 جزوات ویژه", callback_data="vip_files")],
        [InlineKeyboardButton(text="📝 آزمون ویژه", callback_data="vip_quiz")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_to_main")]
    ])

# === روت‌ها ===
router = Router()

class SupportState(StatesGroup):
    msg = State()

@router.message(Command("start"))
async def start_cmd(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer_photo(
        photo="https://img.freepik.com/free-vector/flat-design-nurse-concept-illustration_23-2149185896.jpg",
        caption=f"🌸 *سلام {message.from_user.first_name} عزیز!*\n\n👩‍⚕️ به آکادمی پرستاری خوش آمدید!",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_main")
async def go_back(callback: CallbackQuery):
    await callback.message.edit_text("✨ منوی اصلی:", reply_markup=main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "sub_health")
async def sh_health(callback: CallbackQuery):
    await callback.message.edit_text("🌿 پرستاری سلامت:", reply_markup=health_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "sub_general")
async def sh_general(callback: CallbackQuery):
    await callback.message.edit_text("📖 دروس عمومی:", reply_markup=general_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "sub_basic")
async def sh_basic(callback: CallbackQuery):
    await callback.message.edit_text("🧬 علوم پایه:", reply_markup=basic_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "sub_practice")
async def sh_practice(callback: CallbackQuery):
    await callback.message.edit_text("🏥 پراتیک:", reply_markup=practice_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "sub_vip")
async def sh_vip(callback: CallbackQuery):
    await callback.message.edit_text("👑 VIP:", reply_markup=vip_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("health_"))
async def health_sub(callback: CallbackQuery):
    t = "پرستاری سلامت"
    if callback.data == "health_ind": t += " - فرد"
    elif callback.data == "health_env": t += " - محیط"
    elif callback.data == "health_soc": t += " - جامعه"
    await callback.message.edit_text(f"📖 *{t}*\n\nاطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("gen_"))
async def general_sub(callback: CallbackQuery):
    t = "دروس عمومی"
    if callback.data == "gen_psych": t += " - روان عمومی"
    elif callback.data == "gen_lang": t += " - زبان تخصصی"
    elif callback.data == "gen_rel": t += " - معارف"
    elif callback.data == "gen_lit": t += " - ادبیات"
    elif callback.data == "gen_pe": t += " - تربیت بدنی"
    await callback.message.edit_text(f"📖 *{t}*\n\nاطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("bas_"))
async def basic_sub(callback: CallbackQuery):
    t = "علوم پایه"
    if callback.data == "bas_nut": t += " - تغذیه"
    elif callback.data == "bas_phar": t += " - فارماکولوژی"
    elif callback.data == "bas_par": t += " - انگل‌شناسی"
    elif callback.data == "bas_phy": t += " - فیزیологی"
    elif callback.data == "bas_ana": t += " - آناتومی"
    elif callback.data == "bas_bio": t += " - بیوشیمی"
    elif callback.data == "bas_epi": t += " - اپیدمیولوژی"
    elif callback.data == "bas_imm": t += " - ایمنولوژی"
    elif callback.data == "bas_mic": t += " - میکروب‌شناسی"
    await callback.message.edit_text(f"📖 *{t}*\n\nاطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("pra_"))
async def practice_sub(callback: CallbackQuery):
    t = "پراتیک و کارآموزی"
    if callback.data == "pra_cli": t += " - پراتیک"
    elif callback.data == "pra_int": t += " - کارآموزی"
    await callback.message.edit_text(f"📖 *{t}*\n\nاطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("vip_"))
async def vip_sub(callback: CallbackQuery):
    t = "اشتراک ویژه"
    if callback.data == "vip_teach": t += " - تدریس"
    elif callback.data == "vip_files": t += " - جزوات ویژه"
    elif callback.data == "vip_quiz": t += " - آزمون ویژه"
    await callback.message.edit_text(f"👑 *{t}*\n\nاطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "contact_instructor")
async def contact_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📞 لطفاً پیام خود را بنویسید و بفرستید:", reply_markup=back_btn())
    await state.set_state(SupportState.msg)
    await callback.answer()

@router.message(SupportState.msg)
async def recv_support(message: Message, state: FSMContext):
    await message.bot.send_message(ADMIN_ID, f"📩 پیام جدید از {message.from_user.id}:\n{message.text}")
    await state.clear()
    await message.answer("✅ پیام شما ارسال شد.", reply_markup=back_btn())

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("👑 پنل ادمین:\nیک فایل PDF بفرستید و در کپشن بنویسید `fundamentals`.", parse_mode="Markdown")

@router.message(F.document)
async def get_file(message: Message):
    if message.from_user.id != ADMIN_ID: return
    if not message.caption: return
    save_file(message.caption.strip().lower(), message.document.file_id)
    await message.answer("✅ فایل ذخیره شد!")

# === اجرا ===
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
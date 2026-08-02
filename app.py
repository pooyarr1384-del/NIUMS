import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID

# ==========================================
# 1. دیتابیس
# ==========================================
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS menu_buttons (id INTEGER PRIMARY KEY, parent TEXT, text TEXT, callback TEXT, content TEXT, file_id TEXT)')
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

def add_menu_button(parent, text, callback, content="اطلاعات در حال به‌روزرسانی.", file_id=""):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO menu_buttons (parent, text, callback, content, file_id) VALUES (?, ?, ?, ?, ?)', (parent, text, callback, content, file_id))
    conn.commit()
    conn.close()

def get_buttons(parent):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT text, callback, content, file_id FROM menu_buttons WHERE parent = ?', (parent,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_button_content(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('SELECT content, file_id FROM menu_buttons WHERE callback = ?', (callback,))
    row = c.fetchone()
    conn.close()
    return row if row else ("اطلاعات در دسترس نیست", "")

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

def delete_button(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM menu_buttons WHERE callback = ?', (callback,))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. تنظیم دکمه‌های اولیه
# ==========================================
def init_default_buttons():
    if not get_buttons("main"):
        # دکمه‌های اصلی
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

        # زیرمنوی پرستاری سلامت
        add_menu_button("sub_health", "👤 فرد", "health_ind")
        add_menu_button("sub_health", "🏠 محیط", "health_env")
        add_menu_button("sub_health", "🌍 جامعه", "health_soc")

        # زیرمنوی عمومی/زبان
        add_menu_button("sub_general", "🧠 روان عمومی", "gen_psych")
        add_menu_button("sub_general", "🗣️ زبان تخصصی", "gen_lang")
        add_menu_button("sub_general", "📖 معارف", "gen_rel")
        add_menu_button("sub_general", "✍️ ادبیات", "gen_lit")
        add_menu_button("sub_general", "🏃 تربیت بدنی", "gen_pe")

        # زیرمنوی علوم پایه
        add_menu_button("sub_basic_science", "🥗 تغذیه", "bas_nut")
        add_menu_button("sub_basic_science", "💊 فارماکولوژی", "bas_phar")
        add_menu_button("sub_basic_science", "🔬 انگل‌شناسی", "bas_par")
        add_menu_button("sub_basic_science", "❤️ فیزیولوژی", "bas_phy")
        add_menu_button("sub_basic_science", "🦴 آناتومی", "bas_ana")
        add_menu_button("sub_basic_science", "🧪 بیوشیمی", "bas_bio")
        add_menu_button("sub_basic_science", "📈 اپیدمیولوژی", "bas_epi")
        add_menu_button("sub_basic_science", "🛡️ ایمنولوژی", "bas_imm")
        add_menu_button("sub_basic_science", "🦠 میکروب‌شناسی", "bas_mic")

        # زیرمنوی پراتیک و کارآموزی
        add_menu_button("sub_practice", "🩺 پراتیک", "pra_cli")
        add_menu_button("sub_practice", "🏥 کارآموزی", "pra_int")

        # زیرمنوی VIP
        add_menu_button("sub_vip", "👨‍🏫 تدریس", "vip_teach")
        add_menu_button("sub_vip", "📂 جزوات ویژه", "vip_files")
        add_menu_button("sub_vip", "📝 آزمون ویژه", "vip_quiz")

        # زیرمنوی آزمون‌ها
        add_menu_button("quizzes", "📝 آزمون اصول و فنون", "quiz_fundamentals")

init_default_buttons()

# ==========================================
# 3. ساخت کیبورد
# ==========================================
def build_keyboard(parent, show_back=True):
    buttons = get_buttons(parent)
    keyboard = []
    row = []
    for i, btn in enumerate(buttons):
        text = btn[0]
        callback = btn[1]
        row.append(InlineKeyboardButton(text=text, callback_data=callback))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    if show_back:
        keyboard.append([InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])

# ==========================================
# 4. روت‌های کاربران
# ==========================================
router = Router()

class SupportState(StatesGroup):
    msg = State()

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

@router.callback_query(F.data.startswith(("sub_", "health_", "gen_", "bas_", "pra_", "vip_", "quiz_")))
async def handle_dynamic_buttons(callback: CallbackQuery):
    data = callback.data
    if data in ["sub_health", "sub_general", "sub_basic_science", "sub_practice", "sub_vip", "quizzes"]:
        await callback.message.answer("📂 منوی مربوطه:", reply_markup=build_keyboard(data), parse_mode="Markdown")
        await callback.answer()
        return
    content, file_id = get_button_content(data)
    if file_id:
        await callback.message.answer_document(document=file_id, caption=content, parse_mode="Markdown")
    else:
        await callback.message.answer(content, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "contact_instructor")
async def contact_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📞 لطفاً پیام خود را بنویسید و بفرستید:", reply_markup=back_btn())
    await state.set_state(SupportState.msg)
    await callback.answer()

@router.message(SupportState.msg)
async def recv_support(message: Message, state: FSMContext):
    await message.bot.send_message(ADMIN_ID, f"📩 پیام جدید از {message.from_user.id}:\n{message.text}")
    await state.clear()
    await message.answer("✅ پیام شما ارسال شد.", reply_markup=back_btn())

@router.callback_query(F.data == "about_us")
async def about_us(callback: CallbackQuery):
    content, _ = get_button_content("about_us")
    await callback.message.answer(content, reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

# ==========================================
# 5. پنل ادمین حرفه‌ای و هوشمند
# ==========================================
class AdminState(StatesGroup):
    waiting_for_new_text = State()
    waiting_for_file = State()

SUB_MENUS = {
    "main": "منوی اصلی",
    "sub_health": "زیرمنوی پرستاری سلامت",
    "sub_general": "زیرمنوی دروس عمومی/زبان",
    "sub_basic_science": "زیرمنوی علوم پایه",
    "sub_practice": "زیرمنوی پراتیک و کارآموزی",
    "sub_vip": "زیرمنوی VIP",
    "quizzes": "زیرمنوی آزمون‌ها"
}

def build_admin_submenu_keyboard():
    keyboard = []
    for key, title in SUB_MENUS.items():
        keyboard.append([InlineKeyboardButton(text=f"📂 {title}", callback_data=f"adm_menu_{key}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 ویرایش متن یک دکمه", callback_data="admin_edit_text")],
        [InlineKeyboardButton(text="📎 آپلود فایل برای یک دکمه", callback_data="admin_upload_file")],
        [InlineKeyboardButton(text="📋 مشاهده لیست دکمه‌ها", callback_data="admin_list_buttons")]
    ])
    
    await message.answer("👑 *پنل مدیریت هوشمند*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=keyboard, parse_mode="Markdown")

# 5-1. لیست دکمه‌ها
@router.callback_query(F.data == "admin_list_buttons")
async def admin_list_buttons(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    
    text = "📋 *لیست تمام دکمه‌ها و کدهایشان:*\n\n"
    for key, title in SUB_MENUS.items():
        text += f"\n🔹 *{title}:*\n"
        buttons = get_buttons(key)
        if not buttons:
            text += "   (خالی)\n"
        for btn in buttons:
            text += f"   ➜ {btn[0]} → `{btn[1]}`\n"
    
    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

# 5-2. ویرایش متن
@router.callback_query(F.data == "admin_edit_text")
async def admin_edit_start(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📂 *کدام منو را می‌خواهید ویرایش کنید؟*", reply_markup=build_admin_submenu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("adm_menu_"))
async def admin_edit_select_menu(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
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

@router.callback_query(F.data.startswith("edit_"))
async def admin_edit_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    callback_data = callback.data.replace("edit_", "")
    await state.set_state(AdminState.waiting_for_new_text)
    await state.update_data(target_callback=callback_data)
    await callback.message.answer(f"📝 کد دکمه `{callback_data}` انتخاب شد.\n\n👉 حالا *متن جدید* را بفرستید:")
    await callback.answer()

@router.message(AdminState.waiting_for_new_text)
async def admin_save_text(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    update_button_text(data['target_callback'], message.text)
    await state.clear()
    await message.answer("✅ متن با موفقیت تغییر کرد!")

# 5-3. آپلود فایل
@router.callback_query(F.data == "admin_upload_file")
async def admin_upload_start(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID: return
    await callback.message.answer("📂 *برای کدام منو می‌خواهید فایل آپلود کنید؟*", reply_markup=build_admin_submenu_keyboard(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("adm_menu_"))
async def admin_upload_select_menu(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
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

@router.callback_query(F.data.startswith("upload_"))
async def admin_upload_selected(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    callback_data = callback.data.replace("upload_", "")
    await state.set_state(AdminState.waiting_for_file)
    await state.update_data(target_callback=callback_data)
    await callback.message.answer(f"📎 کد دکمه `{callback_data}` انتخاب شد.\n\n👉 حالا فایل (PDF) را بفرستید:")
    await callback.answer()

@router.message(AdminState.waiting_for_file)
async def admin_save_file(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    if not message.document:
        await message.answer("❌ لطفاً یک فایل بفرستید.")
        return
    data = await state.get_data()
    update_button_file(data['target_callback'], message.document.file_id)
    await state.clear()
    await message.answer("✅ فایل با موفقیت آپلود شد!")

# ==========================================
# 6. اجرا
# ==========================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

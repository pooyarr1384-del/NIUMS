import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID

# ==========================================
# 1. دیتابیس پیشرفته (برای ذخیره دکمه‌ها و محتوا)
# ==========================================
def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    # جدول کاربران
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT)')
    # جدول دکمه‌های منو (مدیریت محتوا از تلگرام)
    c.execute('CREATE TABLE IF NOT EXISTS menu_buttons (id INTEGER PRIMARY KEY, parent TEXT, text TEXT, callback TEXT, content TEXT, file_id TEXT)')
    conn.commit()
    conn.close()

# توابع کاربران
def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
    except: pass
    finally: conn.close()

# توابع مدیریت دکمه‌ها و محتوا
def add_menu_button(parent, text, callback, content="اطلاعات این بخش در حال به‌روزرسانی است.", file_id=""):
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

def delete_button(callback):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('DELETE FROM menu_buttons WHERE callback = ?', (callback,))
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. تنظیم دکمه‌های اولیه (اگر دیتابیس خالی است)
# ==========================================
def init_default_buttons():
    if not get_buttons("main"):
        # دکمه‌های اصلی
        add_menu_button("main", "🫀 داخلی - جراحی", "sub_internal", "📖 *داخلی - جراحی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🍼 کودکان", "sub_pediatric", "📖 *کودکان*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "👴 سالمندان", "sub_geriatric", "📖 *سالمندان*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🤱 مادر و نوزاد", "sub_obstetric", "📖 *مادر و نوزاد*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🧠 روان پرستاری", "sub_psychiatry", "📖 *روان پرستاری*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🌿 پرستاری سلامت", "sub_health", "🌿 *پرستاری سلامت*\n\nیکی از حوزه‌های زیر را انتخاب کنید:", "")
        add_menu_button("main", "🩺 پرستاری بهداشت", "sub_hygiene", "📖 *پرستاری بهداشت*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "💉 مراقبت‌های ویژه", "sub_icu", "📖 *مراقبت‌های ویژه*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🚑 فوریت‌های پزشکی", "sub_emergency", "📖 *فوریت‌های پزشکی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "📋 فرایندهای پرستاری", "sub_process", "📖 *فرایندهای پرستاری*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "📚 رفرنس‌های پرستاری", "sub_references", "📖 *رفرنس‌های پرستاری*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("main", "🧬 علوم پایه", "sub_basic_science", "🧬 *علوم پایه*\n\nیکی از دروس زیر را انتخاب کنید:", "")
        add_menu_button("main", "📖 دروس عمومی/زبان", "sub_general", "📖 *دروس عمومی/زبان*\n\nیکی از دروس زیر را انتخاب کنید:", "")
        add_menu_button("main", "🏥 پراتیک و کارآموزی", "sub_practice", "🏥 *پراتیک و کارآموزی*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", "")
        add_menu_button("main", "🎓 آزمون‌ها", "quizzes", "🎓 *آزمون‌های تمرینی*\n\nیکی از آزمون‌های زیر را انتخاب کنید:", "")
        add_menu_button("main", "📞 پشتیبانی", "contact_instructor", "📞 *پشتیبانی*\n\nلطفاً پیام خود را بنویسید و بفرستید.", "")
        add_menu_button("main", "👑 VIP", "sub_vip", "👑 *VIP (اشتراک ویژه)*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", "")
        add_menu_button("main", "🏥 درباره ما", "about_us", "🏥 *درباره ما*\n\nما یک تیم حرفه‌ای از اساتید و پرستاران با تجربه هستیم.", "")
        
        # زیردکمه‌های پرستاری سلامت
        add_menu_button("sub_health", "👤 فرد", "health_ind", "👤 *پرستاری سلامت - فرد*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_health", "🏠 محیط", "health_env", "🏠 *پرستاری سلامت - محیط*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_health", "🌍 جامعه", "health_soc", "🌍 *پرستاری سلامت - جامعه*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        
        # زیردکمه‌های عمومی
        add_menu_button("sub_general", "🧠 روان عمومی", "gen_psych", "🧠 *روان عمومی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_general", "🗣️ زبان تخصصی", "gen_lang", "🗣️ *زبان تخصصی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_general", "📖 معارف", "gen_rel", "📖 *معارف*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_general", "✍️ ادبیات", "gen_lit", "✍️ *ادبیات*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_general", "🏃 تربیت بدنی", "gen_pe", "🏃 *تربیت بدنی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        
        # زیردکمه‌های علوم پایه
        add_menu_button("sub_basic_science", "🥗 تغذیه", "bas_nut", "🥗 *تغذیه*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "💊 فارماکولوژی", "bas_phar", "💊 *فارماکولوژی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "🔬 انگل‌شناسی", "bas_par", "🔬 *انگل‌شناسی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "❤️ فیزیولوژی", "bas_phy", "❤️ *فیزیولوژی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "🦴 آناتومی", "bas_ana", "🦴 *آناتومی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "🧪 بیوشیمی", "bas_bio", "🧪 *بیوشیمی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "📈 اپیدمیولوژی", "bas_epi", "📈 *اپیدمیولوژی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "🛡️ ایمنولوژی", "bas_imm", "🛡️ *ایمنولوژی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_basic_science", "🦠 میکروب‌شناسی", "bas_mic", "🦠 *میکروب‌شناسی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        
        # زیردکمه‌های پراتیک
        add_menu_button("sub_practice", "🩺 پراتیک", "pra_cli", "🩺 *پراتیک*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_practice", "🏥 کارآموزی", "pra_int", "🏥 *کارآموزی*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        
        # زیردکمه‌های VIP
        add_menu_button("sub_vip", "👨‍🏫 تدریس", "vip_teach", "👨‍🏫 *تدریس*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_vip", "📂 جزوات ویژه", "vip_files", "📂 *جزوات ویژه*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        add_menu_button("sub_vip", "📝 آزمون ویژه", "vip_quiz", "📝 *آزمون ویژه*\n\nاطلاعات این بخش در حال به‌روزرسانی است.")
        
        # زیردکمه‌های آزمون
        add_menu_button("quizzes", "📝 آزمون اصول و فنون", "quiz_fundamentals", "🧪 این آزمون در حال ساخت است.")

init_default_buttons()

# ==========================================
# 3. ساخت کیبوردهای داینامیک بر اساس دیتابیس
# ==========================================
def build_keyboard(parent, show_back=True):
    buttons = get_buttons(parent)
    keyboard = []
    row = []
    for i, btn in enumerate(buttons):
        text = btn[0]
        callback = btn[1]
        row.append(InlineKeyboardButton(text=text, callback_data=callback))
        # دکمه‌ها را دو به دو بچین
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    if show_back:
        keyboard.append([InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ==========================================
# 4. روت‌های ربات
# ==========================================
router = Router()

class SupportState(StatesGroup):
    msg = State()

@router.message(Command("start"))
async def start_cmd(message: Message):
    add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    main_menu = build_keyboard("main")
    await message.answer_photo(
        photo="https://img.freepik.com/free-vector/flat-design-nurse-concept-illustration_23-2149185896.jpg",
        caption=f"🌸 *سلام {message.from_user.first_name} عزیز!*\n\n👩‍⚕️ به آکادمی پرستاری خوش آمدید!\nارائه بهترین محتویات آموزشی ویژه دانشجویان پرستاری\n┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n🏛️ *دانشگاه علوم پزشکی ایران*\nپیشگام در آموزش نوین",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_main")
async def go_back(callback: CallbackQuery):
    await callback.message.answer("✨ منوی اصلی:", reply_markup=build_keyboard("main"), parse_mode="Markdown")
    await callback.answer()

# هندلر کلیک روی دکمه‌ها (مدیریت محتوا از دیتابیس)
@router.callback_query(F.data.startswith(("sub_", "health_", "gen_", "bas_", "pra_", "vip_", "quiz_")))
async def handle_dynamic_buttons(callback: CallbackQuery):
    data = callback.data
    
    # اگر دکمه والد باشد (زیرمنو دارد)، زیرمنو را نشان بده
    if data in ["sub_health", "sub_general", "sub_basic_science", "sub_practice", "sub_vip", "quizzes"]:
        await callback.message.answer("📂 منوی مربوطه:", reply_markup=build_keyboard(data), parse_mode="Markdown")
        await callback.answer()
        return

    # اگر دکمه نهایی باشد، محتوای آن را از دیتابیس بخوان
    content, file_id = get_button_content(data)
    
    # اگر فایلی برای این دکمه آپلود شده باشد، آن را بفرست
    if file_id:
        await callback.message.answer_document(document=file_id, caption=content, parse_mode="Markdown")
    else:
        await callback.message.answer(content, parse_mode="Markdown")
    
    await callback.answer()

# هندلر ارتباط با ادمین
@router.callback_query(F.data == "contact_instructor")
async def contact_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📞 لطفاً پیام خود را بنویسید و بفرستید:", reply_markup=back_btn())
    await state.set_state(SupportState.msg)
    await callback.answer()

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])

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
# 5. پنل ادمین پیشرفته (مدیریت محتوا از تلگرام)
# ==========================================
class AdminState(StatesGroup):
    waiting_for_callback = State()
    waiting_for_new_text = State()
    waiting_for_file = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    
    text = (
        "👑 *پنل مدیریت پیشرفته*\n\n"
        "شما می‌توانید تمام محتوای ربات را از اینجا مدیریت کنید.\n\n"
        "🔹 **برای تغییر متن یک دکمه:**\n"
        "`/edit_text [callback_data]`\n"
        "مثال: `/edit_text sub_internal`\n\n"
        "🔹 **برای آپلود فایل برای یک دکمه خاص:**\n"
        "`/upload_file [callback_data]`\n"
        "مثال: `/upload_file quiz_fundamentals`\n\n"
        "🔹 **برای مشاهده لیست همه دکمه‌ها و callbackها:**\n"
        "`/list_buttons`\n\n"
        "🔹 **برای حذف یک دکمه:**\n"
        "`/delete_button [callback_data]`"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("list_buttons"))
async def list_buttons(message: Message):
    if message.from_user.id != ADMIN_ID: return
    
    buttons = get_buttons("main")
    response = "📋 *لیست دکمه‌های منوی اصلی:*\n\n"
    for btn in buttons:
        response += f"🔹 متن: `{btn[0]}` | کد: `{btn[1]}`\n"
    
    buttons = get_buttons("sub_health")
    response += "\n📋 *زیرمنوی پرستاری سلامت:*\n"
    for btn in buttons:
        response += f"🔹 متن: `{btn[0]}` | کد: `{btn[1]}`\n"
    
    await message.answer(response, parse_mode="Markdown")

@router.message(Command("edit_text"))
async def edit_text_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ لطفاً کد دکمه را وارد کنید.\nمثال: `/edit_text sub_internal`")
        return
    
    callback = parts[1].strip()
    content, _ = get_button_content(callback)
    await message.answer(f"📝 متن فعلی برای `{callback}`:\n\n{content}\n\n👉 حالا متن جدید را بفرستید:")
    await state.set_state(AdminState.waiting_for_new_text)
    await state.update_data(target_callback=callback)

@router.message(AdminState.waiting_for_new_text)
async def save_new_text(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    data = await state.get_data()
    callback = data['target_callback']
    new_text = message.text
    
    # بروزرسانی در دیتابیس
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE menu_buttons SET content = ? WHERE callback = ?', (new_text, callback))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"✅ متن دکمه `{callback}` با موفقیت تغییر کرد!")

@router.message(Command("upload_file"))
async def upload_file_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ لطفاً کد دکمه را وارد کنید.\nمثال: `/upload_file quiz_fundamentals`")
        return
    
    callback = parts[1].strip()
    await message.answer(f"📎 کد دکمه `{callback}` ثبت شد.\n👉 حالا فایل (PDF/عکس) مورد نظر را بفرستید:")
    await state.set_state(AdminState.waiting_for_file)
    await state.update_data(target_callback=callback)

@router.message(AdminState.waiting_for_file)
async def save_uploaded_file(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    if not message.document:
        await message.answer("❌ لطفاً یک فایل ارسال کنید.")
        return
    
    data = await state.get_data()
    callback = data['target_callback']
    file_id = message.document.file_id
    
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('UPDATE menu_buttons SET file_id = ? WHERE callback = ?', (file_id, callback))
    conn.commit()
    conn.close()
    
    await state.clear()
    await message.answer(f"✅ فایل برای دکمه `{callback}` با موفقیت ذخیره شد! کاربران حالا می‌توانند آن را دانلود کنند.")

@router.message(Command("delete_button"))
async def delete_button_cmd(message: Message):
    if message.from_user.id != ADMIN_ID: return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ لطفاً کد دکمه را وارد کنید.\nمثال: `/delete_button sub_internal`")
        return
    
    callback = parts[1].strip()
    delete_button(callback)
    await message.answer(f"✅ دکمه با کد `{callback}` حذف شد.")

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

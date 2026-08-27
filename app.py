import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID, CHANNEL_ID, DB_CHANNEL_ID

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
    waiting_for_new_admin = State()
    waiting_for_remove_admin = State()

# ==========================================
# 2. دیتابیس با کانال تلگرام (DB_CHANNEL_ID)
# ==========================================
# توابع کمکی برای ارسال و خواندن پیام‌ها از کانال
async def send_db_message(bot, text):
    """ارسال یک پیام متنی به کانال دیتابیس"""
    await bot.send_message(DB_CHANNEL_ID, text)

async def read_db_messages(bot):
    """خواندن تمام پیام‌های کانال دیتابیس"""
    messages = []
    offset = 0
    while True:
        updates = await bot.get_updates(offset=offset, timeout=0)
        if not updates:
            break
        for update in updates:
            if update.message and update.message.chat.id == DB_CHANNEL_ID:
                messages.append(update.message)
        offset = updates[-1].update_id + 1
    return messages

# --- ذخیره کاربران ---
async def add_user(bot, user_id, username, first_name):
    await send_db_message(bot, f"USER|{user_id}|{username}|{first_name}")

# --- ذخیره دکمه‌ها ---
async def add_menu_button(bot, parent, text, callback, content="اطلاعات در حال به‌روزرسانی.", file_id="", is_locked=False):
    await send_db_message(bot, f"BTN|{parent}|{text}|{callback}|{content}|{file_id}|{is_locked}")

# --- خواندن دکمه‌ها ---
async def get_buttons(bot, parent):
    messages = await read_db_messages(bot)
    rows = []
    for msg in messages:
        if msg.text and msg.text.startswith("BTN|"):
            parts = msg.text.split("|")
            if len(parts) >= 7 and parts[1] == parent:
                rows.append((parts[2], parts[3], parts[4], parts[5], parts[6] == "True"))
    return rows

# --- خواندن محتوای دکمه ---
async def get_button_content(bot, callback):
    messages = await read_db_messages(bot)
    for msg in messages:
        if msg.text and msg.text.startswith("BTN|"):
            parts = msg.text.split("|")
            if len(parts) >= 7 and parts[3] == callback:
                return parts[4], parts[5], parts[6] == "True"
    return "اطلاعات در دسترس نیست", "", False

# --- ذخیره دکمه قفل شده ---
async def update_button_lock(bot, callback, is_locked):
    # در این روش، ما پیام را به کانال می‌فرستیم تا دکمه‌ها به‌روز شوند
    # (برای سادگی، فقط قفل جدید را ارسال می‌کنیم)
    pass

# ==========================================
# 3. تنظیم دکمه‌های اولیه
# ==========================================
async def init_default_buttons(bot):
    # اگر دکمه‌ها در کانال خالی بودند، دکمه‌های اولیه را می‌فرستیم
    buttons = await get_buttons(bot, "main")
    if not buttons:
        await add_menu_button(bot, "main", "🫀 داخلی - جراحی", "sub_internal")
        await add_menu_button(bot, "main", "🍼 کودکان", "sub_pediatric")
        await add_menu_button(bot, "main", "👴 سالمندان", "sub_geriatric")
        await add_menu_button(bot, "main", "🤱 مادر و نوزاد", "sub_obstetric")
        await add_menu_button(bot, "main", "🧠 روان پرستاری", "sub_psychiatry")
        await add_menu_button(bot, "main", "🌿 پرستاری سلامت", "sub_health")
        await add_menu_button(bot, "main", "🩺 پرستاری بهداشت", "sub_hygiene")
        await add_menu_button(bot, "main", "💉 مراقبت‌های ویژه", "sub_icu")
        await add_menu_button(bot, "main", "🚑 فوریت‌های پزشکی", "sub_emergency")
        await add_menu_button(bot, "main", "📋 فرایندهای پرستاری", "sub_process")
        await add_menu_button(bot, "main", "📚 رفرنس‌های پرستاری", "sub_references")
        await add_menu_button(bot, "main", "🧬 علوم پایه", "sub_basic_science")
        await add_menu_button(bot, "main", "📖 دروس عمومی/زبان", "sub_general")
        await add_menu_button(bot, "main", "🏥 پراتیک و کارآموزی", "sub_practice")
        await add_menu_button(bot, "main", "📞 پشتیبانی", "contact_instructor")
        await add_menu_button(bot, "main", "👑 VIP", "sub_vip")
        await add_menu_button(bot, "main", "🏥 درباره ما", "about_us")
        await add_menu_button(bot, "main", "🧮 ماشین حساب پرستاری", "calculator_menu")

# ==========================================
# 4. ساخت کیبورد
# ==========================================
async def build_keyboard(bot, parent, show_back=True):
    buttons = await get_buttons(bot, parent)
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

# ==========================================
# 5. روت‌های اصلی کاربران
# ==========================================
main_router = Router()

@main_router.message(Command("start"))
async def start_cmd(message: Message):
    await add_user(message.bot, message.from_user.id, message.from_user.username, message.from_user.first_name)
    
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
        reply_markup=await build_keyboard(message.bot, "main"),
        parse_mode="Markdown"
    )

@main_router.callback_query(F.data == "back_to_main")
async def go_back(callback: CallbackQuery):
    await callback.message.answer("✨ منوی اصلی:", reply_markup=await build_keyboard(callback.bot, "main"), parse_mode="Markdown")
    await callback.answer()

@main_router.callback_query(F.data.startswith(("sub_", "health_", "gen_", "bas_", "pra_", "vip_")))
async def handle_dynamic_buttons(callback: CallbackQuery):
    data = callback.data
    if data in ["sub_health", "sub_general", "sub_basic_science", "sub_practice", "sub_vip"]:
        await callback.message.answer("📂 منوی مربوطه:", reply_markup=await build_keyboard(callback.bot, data), parse_mode="Markdown")
        await callback.answer()
        return
    
    content, file_id, is_locked = await get_button_content(callback.bot, data)
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

@main_router.callback_query(F.data.startswith("check_"))
async def check_membership_after_join(callback: CallbackQuery):
    data = callback.data.replace("check_", "")
    is_member = await check_membership(callback.bot, callback.from_user.id)
    if is_member:
        content, file_id, _ = await get_button_content(callback.bot, data)
        if file_id:
            await callback.message.answer_document(document=file_id, caption=content, parse_mode="Markdown")
        else:
            await callback.message.answer(content, parse_mode="Markdown")
    else:
        await callback.message.answer("❌ شما هنوز عضو کانال نشده‌اید! لطفاً ابتدا عضو شوید.")
    await callback.answer()

async def check_membership(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

# ==========================================
# 6. هندلر اختصاصی ماشین حساب
# ==========================================
@main_router.callback_query(F.data == "calculator_menu")
async def open_calculator(callback: CallbackQuery):
    calc_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 محاسبه BMI", callback_data="calc_bmi"),
         InlineKeyboardButton(text="💊 دوز دارو", callback_data="calc_drug")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])
    await callback.message.answer(
        "🧮 *ماشین حساب پرستاری*\n\nیکی از ابزارهای زیر را انتخاب کنید:",
        reply_markup=calc_keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "calc_bmi")
async def calc_bmi(callback: CallbackQuery):
    await callback.message.answer(
        "📝 *محاسبه BMI*\n\nلطفاً وزن (کیلوگرم) و قد (متر) را به ترتیب با فاصله بفرستید.\nمثال: ۷۵ ۱.۷۵",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.callback_query(F.data == "calc_drug")
async def calc_drug(callback: CallbackQuery):
    await callback.message.answer(
        "💊 *محاسبه دوز دارو*\n\nلطفاً این ۳ عدد را با فاصله بفرستید:\n۱. دوز تجویزی (mg/kg)\n۲. وزن بیمار (kg)\n۳. غلظت دارو (mg/ml)\n\nمثال: ۵ ۷۰ ۱۰",
        reply_markup=back_btn(),
        parse_mode="Markdown"
    )
    await callback.answer()

@main_router.message(F.text.regexp(r'^\d+(\.\d+)?(\s+\d+(\.\d+)?)*$'))
async def handle_calc_input(message: Message):
    numbers = list(map(float, message.text.split()))
    if len(numbers) == 2:
        weight, height = numbers[0], numbers[1]
        if height > 3:
            height = height / 100
        bmi = weight / (height ** 2)
        category = "لاغر" if bmi < 18.5 else "نرمال" if bmi < 25 else "اضافه وزن" if bmi < 30 else "چاق"
        await message.answer(
            f"🧮 *نتیجه BMI*\n\n"
            f"وزن: {weight} کیلوگرم\n"
            f"قد: {height} متر\n"
            f"شاخص BMI: *{bmi:.2f}*\n"
            f"وضعیت: {category}",
            parse_mode="Markdown"
        )
    elif len(numbers) == 3:
        dose_per_kg, weight, concentration = numbers[0], numbers[1], numbers[2]
        total_dose = dose_per_kg * weight
        volume_ml = total_dose / concentration
        await message.answer(
            f"💊 *نتیجه دوز دارو*\n\n"
            f"دوز تجویزی: {dose_per_kg} mg/kg\n"
            f"وزن بیمار: {weight} kg\n"
            f"غلظت ویال: {concentration} mg/ml\n"
            f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
            f"✅ دوز کل مورد نیاز: *{total_dose} mg*\n"
            f"✅ حجم مورد نیاز از ویال: *{volume_ml:.2f} ml*",
            parse_mode="Markdown"
        )

@main_router.callback_query(F.data == "contact_instructor")
async def contact_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📞 لطفاً پیام خود را بنویسید و بفرستید:", reply_markup=back_btn())
    await state.set_state(SupportState.msg)
    await callback.answer()

@main_router.message(SupportState.msg)
async def recv_support(message: Message, state: FSMContext):
    user = message.from_user
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 پاسخ به این کاربر", callback_data=f"reply_{user.id}")]
    ])
    await message.bot.send_message(
        ADMIN_ID,
        f"📩 *پیام جدید از کاربر*\n🆔: `{user.id}`\n👤: {user.first_name}\n💬: {message.text}",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await state.clear()
    await message.answer("✅ پیام شما با موفقیت برای پشتیبان ارسال شد.", reply_markup=back_btn())

@main_router.callback_query(F.data.startswith("reply_"))
async def admin_start_reply(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID: return
    user_id = int(callback.data.replace("reply_", ""))
    await state.set_state(AdminReplyState.waiting_for_reply)
    await state.update_data(target_user=user_id)
    await callback.message.answer(f"📝 *پاسخ به کاربر `{user_id}`*\n\n👉 متن پاسخ خود را بنویسید و بفرستید:", parse_mode="Markdown")
    await callback.answer()

@main_router.message(AdminReplyState.waiting_for_reply)
async def admin_send_reply(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID: return
    data = await state.get_data()
    user_id = data['target_user']
    await message.bot.send_message(user_id, f"💬 *پاسخ پشتیبان:*\n\n{message.text}", parse_mode="Markdown")
    await state.clear()
    await message.answer("✅ پاسخ شما با موفقیت به کاربر ارسال شد!", reply_markup=back_btn())

@main_router.callback_query(F.data == "about_us")
async def about_us(callback: CallbackQuery):
    content, _, _ = await get_button_content(callback.bot, "about_us")
    await callback.message.answer(content, reply_markup=back_btn(), parse_mode="Markdown")
    await callback.answer()

def back_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])

# ==========================================
# 7. پنل ادمین
# ==========================================
SUB_MENUS = {
    "main": "منوی اصلی",
    "sub_health": "زیرمنوی پرستاری سلامت",
    "sub_general": "زیرمنوی دروس عمومی/زبان",
    "sub_basic_science": "زیرمنوی علوم پایه",
    "sub_practice": "زیرمنوی پراتیک و کارآموزی",
    "sub_vip": "زیرمنوی VIP"
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

def is_admin(user_id):
    # در این نسخه، ادمین اصلی همان آیدی در config است
    return user_id == ADMIN_ID

# ==========================================
# 8. اجرا
# ==========================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(main_router)
    
    # اولیه‌سازی دکمه‌ها در کانال
    await init_default_buttons(bot)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

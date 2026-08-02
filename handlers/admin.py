from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database.db import save_file

router = Router()

class AdminStates(StatesGroup):
    waiting_for_file_upload = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ شما دسترسی به این بخش ندارید!")
        return
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📎 آپلود فایل جزوه", callback_data="admin_upload_file")]
        ]
    )
    await message.answer("👑 *پنل مدیریت*\n\nبرای آپلود فایل، روی دکمه زیر کلیک کنید:", reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "admin_upload_file")
async def start_upload_file(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📎 *آپلود فایل جزوه*\n\n"
        "۱. یک فایل PDF را انتخاب کنید و بفرستید.\n"
        "۲. در قسمت کپشن (توضیحات) فایل، دقیقاً بنویسید: `fundamentals`",
        parse_mode="Markdown"
    )
    await state.set_state(AdminStates.waiting_for_file_upload)
    await callback.answer()

@router.message(AdminStates.waiting_for_file_upload)
async def receive_uploaded_file(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not message.document:
        await message.answer("❌ شما باید یک فایل (PDF) بفرستید.")
        return
    
    if not message.caption:
        await message.answer("❌ لطفاً در قسمت کپشن فایل، نام درس را بنویسید (مثلاً `fundamentals`).")
        return
    
    file_name = message.caption.strip().lower()
    file_id = message.document.file_id
    
    save_file(file_name, file_id)
    
    await state.clear()
    await message.answer(f"✅ فایل `{file_name}` با موفقیت آپلود شد! حالا کاربران می‌توانند آن را دانلود کنند.")
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.db import add_user
from keyboards.inline import get_main_menu, inline_back_menu, get_quiz_menu, get_pdf_menu, NURSING_SUBJECTS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    main_menu = get_main_menu()
    
    welcome_text = (
        f"🌸 *سلام {message.from_user.first_name} عزیز!*\n\n"
        "👩‍⚕️ به *آکادمی آموزش پرستاری* خوش آمدید!\n"
        "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        "👇 *برای شروع، یکی از دروس زیر را انتخاب کنید:*"
    )
    
    await message.answer(welcome_text, reply_markup=main_menu, parse_mode="Markdown")

@router.callback_query(F.data.startswith("subject_"))
async def show_subject_info(callback: CallbackQuery):
    subject_code = callback.data
    subject_name = "درس"
    for name, code in NURSING_SUBJECTS.items():
        if code == subject_code:
            subject_name = name
            break
    
    info_text = "اطلاعات این درس در حال به‌روزرسانی است."
    if subject_code == "subject_fundamentals":
        info_text = "🏥 *اصول و فنون پرستاری*\n\n📌 *سرفصل‌های مهم:*\n🔹 تکنیک‌های استریل و ضدعفونی\n🔹 تزریقات (عضلانی، وریدی، زیرجلدی)\n🔹 پانسمان و بخیه زدن"
    elif subject_code == "subject_med_surg":
        info_text = "🫀 *پرستاری داخلی - جراحی*\n\n📌 *سرفصل‌های مهم:*\n🔹 مراقبت‌های ICU و CCU\n🔹 بیماری‌های قلبی و تنفسی\n🔹 مراقبت‌های قبل و بعد از عمل جراحی"
    elif subject_code == "subject_pediatric":
        info_text = "🍼 *پرستاری کودکان*\n\n📌 *سرفصل‌های مهم:*\n🔹 اصول مراقبت از نوزاد نارس\n🔹 بیماری‌های شایع کودکان\n🔹 برنامه واکسیناسیون کشوری"
    elif subject_code == "subject_obstetrics":
        info_text = "🤱 *پرستاری مادران و نوزادان*\n\n📌 *سرفصل‌های مهم:*\n🔹 مراقبت‌های دوران بارداری (پره‌ناتال)\n🔹 مراحل زایمان طبیعی و سزارین\n🔹 مراقبت پس از زایمان (پوستال)"
    elif subject_code == "subject_psychiatry":
        info_text = "🧠 *پرستاری سلامت روان*\n\n📌 *سرفصل‌های مهم:*\n🔹 شناخت اختلالات روانپزشکی (افسردگی، اسکیزوفرنی)\n🔹 مهارت‌های ارتباط درمانی با بیمار\n🔹 داروهای روانپزشکی و عوارض آن‌ها"
    elif subject_code == "subject_emergency":
        info_text = "🚑 *فوریت‌های پزشکی (اورژانس)*\n\n📌 *سرفصل‌های مهم:*\n🔹 احیای قلبی ریوی پایه (BLS) و پیشرفته (ACLS)\n🔹 سیستم تریاژ در حوادث\n🔹 مدیریت بیماران ترومایی و سوختگی"
    
    await callback.message.edit_text(
        f"📖 *{subject_name}*\n\n{info_text}\n\n✨ برای بازگشت کلیک کنید:",
        reply_markup=inline_back_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "quizzes")
async def show_quizzes(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎓 *آزمون‌های تمرینی*\n\n🧠 می‌خوای دانشت رو محک بزنی؟ روی آزمون زیر کلیک کن:",
        reply_markup=get_quiz_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "get_pdfs")
async def show_pdf_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 *کتابخانه جزوات (PDF)*\n\nبرای دانلود فایل‌های آموزشی، روی گزینه زیر کلیک کنید:",
        reply_markup=get_pdf_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "pdf_fundamentals")
async def send_pdf_file(callback: CallbackQuery):
    from database.db import get_file_id
    
    file_name = "fundamentals"
    file_id = get_file_id(file_name)
    
    if not file_id:
        await callback.message.edit_text(
            "❌ فایل جزوه هنوز در سیستم آپلود نشده است!\n"
            "لطفاً از طریق پنل ادمین (دکمه آپلود فایل جزوه) این فایل را آپلود کنید.",
            reply_markup=inline_back_menu()
        )
        await callback.answer()
        return

    await callback.message.answer_document(
        document=file_id,
        caption="📄 *جزوه کامل اصول و فنون پرستاری*\n\n✅ فایل با موفقیت ارسال شد.",
        parse_mode="Markdown",
        reply_markup=inline_back_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "✨ به منوی اصلی بازگشتید! 👇",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()
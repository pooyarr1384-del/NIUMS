from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database.db import add_user, get_file_id
from keyboards.inline import (get_main_menu, back_to_main_menu, get_health_sub_menu, 
                               get_general_sub_menu, get_basic_sub_menu, 
                               get_practice_sub_menu, get_vip_sub_menu,
                               get_quiz_menu, get_pdf_menu, NURSING_SUBJECTS)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    add_user(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name)
    main_menu = get_main_menu()
    photo_url = "https://img.freepik.com/free-vector/flat-design-nurse-concept-illustration_23-2149185896.jpg"
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
    await message.answer_photo(photo=photo_url, caption=caption_text, reply_markup=main_menu, parse_mode="Markdown")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("✨ به منوی اصلی بازگشتید! 👇", reply_markup=get_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "subject_health")
async def show_health_sub(callback: CallbackQuery):
    await callback.message.edit_text("🌿 *پرستاری سلامت*\n\nیکی از حوزه‌های زیر را انتخاب کنید:", reply_markup=get_health_sub_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "subject_general")
async def show_general_sub(callback: CallbackQuery):
    await callback.message.edit_text("📖 *دروس عمومی/زبان*\n\nیکی از دروس زیر را انتخاب کنید:", reply_markup=get_general_sub_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "subject_basic_science")
async def show_basic_sub(callback: CallbackQuery):
    await callback.message.edit_text("🧬 *علوم پایه*\n\nیکی از دروس زیر را انتخاب کنید:", reply_markup=get_basic_sub_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "subject_practice")
async def show_practice_sub(callback: CallbackQuery):
    await callback.message.edit_text("🏥 *پراتیک و کارآموزی*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=get_practice_sub_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "vip")
async def show_vip_sub(callback: CallbackQuery):
    await callback.message.edit_text("👑 *اشتراک ویژه (VIP)*\n\nیکی از گزینه‌های زیر را انتخاب کنید:", reply_markup=get_vip_sub_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "health_ind")
async def show_health_ind(callback: CallbackQuery):
    await callback.message.edit_text("👤 *پرستاری سلامت - فرد*\n\nبررسی عوامل فردی مؤثر بر سلامت و سبک زندگی سالم.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "health_env")
async def show_health_env(callback: CallbackQuery):
    await callback.message.edit_text("🏠 *پرستاری سلامت - محیط*\n\nبررسی تأثیر محیط زندگی و کار بر سلامت جامعه و مداخلات محیطی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "health_soc")
async def show_health_soc(callback: CallbackQuery):
    await callback.message.edit_text("🌍 *پرستاری سلامت - جامعه*\n\nبررسی بهداشت جامعه، آموزش همگانی و کنترل بیماری‌های واگیر.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "general_psych")
async def show_general_psych(callback: CallbackQuery):
    await callback.message.edit_text("🧠 *روان عمومی*\n\nآشنایی با مبانی روانشناسی، مکاتب روانشناسی و کاربرد آن در زندگی روزمره.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "general_lang")
async def show_general_lang(callback: CallbackQuery):
    await callback.message.edit_text("🗣️ *زبان تخصصی/عمومی*\n\nزبان انگلیسی تخصصی پرستاری و اصطلاحات پزشکی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "general_religion")
async def show_general_religion(callback: CallbackQuery):
    await callback.message.edit_text("📖 *معارف*\n\nدروس معارف اسلامی و اخلاق حرفه‌ای در پرستاری.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "general_lit")
async def show_general_lit(callback: CallbackQuery):
    await callback.message.edit_text("✍️ *ادبیات*\n\nمبانی ادبیات فارسی، نگارش و مهارت‌های ارتباطی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "general_pe")
async def show_general_pe(callback: CallbackQuery):
    await callback.message.edit_text("🏃 *تربیت بدنی*\n\nاصول تربیت بدنی، بهداشت ورزش و اهمیت فعالیت بدنی در سلامت.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_nutri")
async def show_basic_nutri(callback: CallbackQuery):
    await callback.message.edit_text("🥗 *تغذیه*\n\nاصول تغذیه در سلامت و بیماری، رژیم‌های درمانی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_pharma")
async def show_basic_pharma(callback: CallbackQuery):
    await callback.message.edit_text("💊 *فارماکولوژی*\n\nداروشناسی، مکانیسم اثر داروها و تداخلات دارویی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_para")
async def show_basic_para(callback: CallbackQuery):
    await callback.message.edit_text("🔬 *انگل‌شناسی*\n\nانگل‌های پزشکی، بیماری‌های ناشی از انگل‌ها.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_phys")
async def show_basic_phys(callback: CallbackQuery):
    await callback.message.edit_text("❤️ *فیزیولوژی*\n\nکارکرد اعضا و دستگاه‌های بدن انسان.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_anat")
async def show_basic_anat(callback: CallbackQuery):
    await callback.message.edit_text("🦴 *آناتومی*\n\nساختار بدن انسان و روابط بین اعضا.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_bioch")
async def show_basic_bioch(callback: CallbackQuery):
    await callback.message.edit_text("🧪 *بیوشیمی*\n\nمبانی شیمی حیات و متابولیسم سلولی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_epi")
async def show_basic_epi(callback: CallbackQuery):
    await callback.message.edit_text("📈 *اپیدمیولوژی*\n\nمطالعه الگوهای بیماری‌ها و روش‌های کنترل آن‌ها.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_immun")
async def show_basic_immun(callback: CallbackQuery):
    await callback.message.edit_text("🛡️ *ایمنولوژی*\n\nسیستم ایمنی بدن و واکنش‌های ایمنی در برابر عوامل بیماری‌زا.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "basic_micro")
async def show_basic_micro(callback: CallbackQuery):
    await callback.message.edit_text("🦠 *میکروب‌شناسی*\n\nمیکروارگانیسم‌های بیماری‌زا و روش‌های مبارزه با آن‌ها.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "practice_clinic")
async def show_practice_clinic(callback: CallbackQuery):
    await callback.message.edit_text("🩺 *پراتیک*\n\nمهارت‌های بالینی عملی، معاینه بیمار و کار با تجهیزات پزشکی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "practice_intern")
async def show_practice_intern(callback: CallbackQuery):
    await callback.message.edit_text("🏥 *کارآموزی*\n\nراهنمای کارآموزی در بیمارستان‌ها و مراکز درمانی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "vip_teach")
async def show_vip_teach(callback: CallbackQuery):
    await callback.message.edit_text("👨‍🏫 *تدریس مطالب پرستاری*\n\nدسترسی به ویدیوها و کلاس‌های آنلاین تدریس مطالب تخصصی پرستاری.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "vip_files")
async def show_vip_files(callback: CallbackQuery):
    await callback.message.edit_text("📂 *جزوات ویژه*\n\nدریافت جزوات اختصاصی و با کیفیت بالا که فقط به اعضای ویژه ارائه می‌شود.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "vip_quiz")
async def show_vip_quiz(callback: CallbackQuery):
    await callback.message.edit_text("📝 *آزمون‌های تخصصی و ویژه*\n\nدسترسی به آزمون‌های پیشرفته و تخصصی با پاسخنامه تشریحی.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("subject_"))
async def show_subject_info(callback: CallbackQuery):
    subject_code = callback.data
    if subject_code in ["subject_health", "subject_general", "subject_basic_science", "subject_practice"]:
        return  
    subject_name = "درس"
    for name, code in NURSING_SUBJECTS.items():
        if code == subject_code:
            subject_name = name
            break
    await callback.message.edit_text(f"📖 *{subject_name}*\n\n📌 اطلاعات این بخش در حال به‌روزرسانی است.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "quizzes")
async def show_quizzes(callback: CallbackQuery):
    await callback.message.edit_text("🎓 *آزمون‌های تمرینی*\n\n🧠 می‌خوای دانشت رو محک بزنی؟ روی آزمون زیر کلیک کن:", reply_markup=get_quiz_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "contact_instructor")
async def start_support(callback: CallbackQuery):
    await callback.message.edit_text("📞 *ارتباط با ادمین*\n\nلطفاً پیام خود را بنویسید و بفرستید.", reply_markup=back_to_main_menu())
    await callback.answer()

@router.callback_query(F.data == "about_us")
async def about_us(callback: CallbackQuery):
    await callback.message.edit_text("🏥 *درباره ما*\n\nما یک تیم حرفه‌ای از اساتید و پرستاران با تجربه هستیم.", reply_markup=back_to_main_menu(), parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "pdf_fundamentals")
async def send_pdf_file(callback: CallbackQuery):
    file_name = "fundamentals"
    file_id = get_file_id(file_name)
    if not file_id:
        await callback.message.edit_text("❌ فایل جزوه هنوز آپلود نشده است!", reply_markup=back_to_main_menu())
        await callback.answer()
        return
    await callback.message.answer_document(document=file_id, caption="📄 *جزوه کامل اصول و فنون پرستاری*\n\n✅ فایل با موفقیت ارسال شد.", parse_mode="Markdown", reply_markup=back_to_main_menu())
    await callback.answer()
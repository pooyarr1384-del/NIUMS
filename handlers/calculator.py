from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.inline import back_to_main_menu

router = Router()

# دیکشنری ماشین حساب
CALC_TYPES = {
    "bmi": "شاخص توده بدنی (BMI)",
    "drug_dose": "محاسبه دوز دارو (بر اساس وزن)",
    "fluid_calc": "محاسبه مایعات وریدی",
    "burn_calc": "محاسبه سطح سوختگی (قانون ۹)"
}

@router.message(Command("calc"))
async def show_calculator_menu(message: Message):
    """نمایش منوی ماشین حساب"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧮 BMI", callback_data="calc_bmi")],
        [InlineKeyboardButton(text="💊 دوز دارو", callback_data="calc_drug")],
        [InlineKeyboardButton(text="💧 مایعات وریدی", callback_data="calc_fluid")],
        [InlineKeyboardButton(text="🔥 سوختگی", callback_data="calc_burn")],
        [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی", callback_data="back_to_main")]
    ])
    await message.answer("🧮 *ماشین حساب پرستاری*\n\nیکی از ابزارهای زیر را انتخاب کنید:", reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "calc_bmi")
async def calc_bmi(callback: CallbackQuery):
    """محاسبه BMI"""
    await callback.message.answer(
        "📝 *محاسبه BMI*\n\nبرای محاسبه شاخص توده بدنی، اطلاعات زیر را به صورت یکی در میان بفرستید:\n\n"
        "۱. فرمول: وزن(kg) / قد(m)²\n"
        "۲. مثال: اگر وزن شما ۷۵ کیلوگرم و قد شما ۱.۷۵ متر است، نتایج را به ما بگویید.\n\n"
        "👉 لطفاً وزن (کیلوگرم) را بفرستید:",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "calc_drug")
async def calc_drug(callback: CallbackQuery):
    await callback.message.answer(
        "💊 *محاسبه دوز دارو*\n\nلطفاً اطلاعات زیر را به ترتیب بفرستید:\n"
        "۱. دوز تجویز شده (mg/kg)\n"
        "۲. وزن بیمار (kg)\n"
        "۳. غلظت دارو در ویال (mg/ml)\n\n"
        "👉 مثال: ۵ ۷۰ ۱۰ (به معنی ۵ میلی‌گرم بر کیلوگرم، ۷۰ کیلوگرم وزن، ویال ۱۰ میلی‌گرم/میلی‌لیتر)\n\n"
        "اعداد را با فاصله بفرستید:",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "calc_fluid")
async def calc_fluid(callback: CallbackQuery):
    await callback.message.answer(
        "💧 *محاسبه مایعات وریدی*\n\nلطفاً وزن بیمار را به کیلوگرم بفرستید.\n\n"
        "👉 فرمول: ۴ml/kg برای ۱۰ کیلوگرم اول + ۲ml/kg برای ۱۰ کیلوگرم دوم + ۱ml/kg برای بقیه.",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "calc_burn")
async def calc_burn(callback: CallbackQuery):
    await callback.message.answer(
        "🔥 *محاسبه سطح سوختگی (قانون ۹)*\n\nلطفاً بخش‌های سوخته بدن را به صورت اعداد زیر بفرستید:\n"
        "سر = ۹, تنه جلو = ۱۸, تنه پشت = ۱۸, هر پا = ۱۸, هر دست = ۹, ناحیه تناسلی = ۱\n\n"
        "👉 مثال: اگر سر و یک دست سوخته است، بنویسید: ۹ ۹",
        parse_mode="Markdown"
    )


@router.message(F.text.regexp(r'^\d+(\.\d+)?(\s+\d+(\.\d+)?)*$'))
async def handle_calc_input(message: Message):
    """دریافت ورودی‌های عددی و محاسبه"""
    numbers = list(map(float, message.text.split()))
    
    if len(numbers) == 1:
        # محاسبه BMI یا مایعات
        # ساده: فرض می‌کنیم کاربر وزن و قد را در دو پیام جداگانه می‌فرستد
        await message.answer("📐 قد خود را به متر بفرستید (مثلاً 1.75):")
    
    elif len(numbers) == 2:
        # محاسبه BMI
        weight, height = numbers[0], numbers[1]
        if height > 3:  # اگر قد به سانتی‌متر وارد شده باشد
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
        # محاسبه دوز دارو
        dose_per_kg, weight, concentration = numbers[0], numbers[1], numbers[2]
        total_dose = dose_per_kg * weight
        volume_ml = total_dose / concentration
        await message.answer(
            f"💊 *محاسبه دوز دارو*\n\n"
            f"دوز تجویزی: {dose_per_kg} mg/kg\n"
            f"وزن بیمار: {weight} kg\n"
            f"غلظت ویال: {concentration} mg/ml\n"
            f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
            f"✅ دوز کل مورد نیاز: *{total_dose} mg*\n"
            f"✅ حجم مورد نیاز از ویال: *{volume_ml:.2f} ml*",
            parse_mode="Markdown"
        )

    elif len(numbers) in [4, 5]:
        # محاسبه مایعات (فرمول هالیدی-سگار)
        weight = numbers[0]
        if weight <= 10:
            fluid = weight * 100
        elif weight <= 20:
            fluid = 1000 + (weight - 10) * 50
        else:
            fluid = 1500 + (weight - 20) * 20
        await message.answer(
            f"💧 *محاسبه مایعات وریدی*\n\n"
            f"وزن بیمار: {weight} kg\n"
            f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
            f"✅ مایعات مورد نیاز روزانه: *{fluid} ml*",
            parse_mode="Markdown"
        )
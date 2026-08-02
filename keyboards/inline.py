from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# دیکشنری دروس اصلی برای منوی اول
NURSING_SUBJECTS = {
    "🫀 داخلی - جراحی": "subject_internal_surg",
    "🍼 کودکان": "subject_pediatric",
    "👴 سالمندان": "subject_geriatric",
    "🤱 مادر و نوزاد": "subject_obstetric",
    "🧠 روان پرستاری": "subject_psychiatry",
    "🌿 پرستاری سلامت": "subject_health",
    "🩺 پرستاری بهداشت": "subject_hygiene",
    "💉 مراقبت‌های ویژه": "subject_icu",
    "🚑 فوریت‌های پزشکی": "subject_emergency",
    "📋 فرایندهای پرستاری": "subject_process",
    "📚 رفرنس‌های پرستاری": "subject_references",
    "🧬 علوم پایه": "subject_basic_science",
    "📖 دروس عمومی/زبان": "subject_general",
    "🏥 پراتیک و کارآموزی": "subject_practice",
}

def get_main_menu():
    """منوی اصلی"""
    keyboard = []
    subjects_list = list(NURSING_SUBJECTS.keys())
    for i in range(0, len(subjects_list), 2):
        row = []
        row.append(InlineKeyboardButton(text=subjects_list[i], callback_data=NURSING_SUBJECTS[subjects_list[i]]))
        if i + 1 < len(subjects_list):
            row.append(InlineKeyboardButton(text=subjects_list[i+1], callback_data=NURSING_SUBJECTS[subjects_list[i+1]]))
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton(text="🎓 آزمون‌های تمرینی", callback_data="quizzes"),
        InlineKeyboardButton(text="📞 ارتباط با ادمین", callback_data="contact_instructor")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🏥 درباره ما", callback_data="about_us"),
        InlineKeyboardButton(text="👑 VIP (اشتراک ویژه)", callback_data="vip")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_main_menu():
    """دکمه بازگشت به منوی اصلی"""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]]
    )

def get_health_sub_menu():
    """زیرمنوی پرستاری سلامت"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 فرد", callback_data="health_ind")],
            [InlineKeyboardButton(text="🏠 محیط", callback_data="health_env")],
            [InlineKeyboardButton(text="🌍 جامعه", callback_data="health_soc")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_general_sub_menu():
    """زیرمنوی دروس عمومی/زبان"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧠 روان عمومی", callback_data="general_psych")],
            [InlineKeyboardButton(text="🗣️ زبان تخصصی/عمومی", callback_data="general_lang")],
            [InlineKeyboardButton(text="📖 معارف", callback_data="general_religion")],
            [InlineKeyboardButton(text="✍️ ادبیات", callback_data="general_lit")],
            [InlineKeyboardButton(text="🏃 تربیت بدنی", callback_data="general_pe")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_basic_sub_menu():
    """زیرمنوی علوم پایه"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🥗 تغذیه", callback_data="basic_nutri")],
            [InlineKeyboardButton(text="💊 فارماکولوژی", callback_data="basic_pharma")],
            [InlineKeyboardButton(text="🔬 انگل‌شناسی", callback_data="basic_para")],
            [InlineKeyboardButton(text="❤️ فیزیولوژی", callback_data="basic_phys")],
            [InlineKeyboardButton(text="🦴 آناتومی", callback_data="basic_anat")],
            [InlineKeyboardButton(text="🧪 بیوشیمی", callback_data="basic_bioch")],
            [InlineKeyboardButton(text="📈 اپیدمیولوژی", callback_data="basic_epi")],
            [InlineKeyboardButton(text="🛡️ ایمنولوژی", callback_data="basic_immun")],
            [InlineKeyboardButton(text="🦠 میکروب‌شناسی", callback_data="basic_micro")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_practice_sub_menu():
    """زیرمنوی پراتیک و کارآموزی"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🩺 پراتیک", callback_data="practice_clinic")],
            [InlineKeyboardButton(text="🏥 کارآموزی", callback_data="practice_intern")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_vip_sub_menu():
    """زیرمنوی VIP"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🏫 تدریس مطالب پرستاری", callback_data="vip_teach")],
            [InlineKeyboardButton(text="📂 جزوات ویژه", callback_data="vip_files")],
            [InlineKeyboardButton(text="📝 آزمون‌های تخصصی و ویژه", callback_data="vip_quiz")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_quiz_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 آزمون اصول و فنون (۳ سوال)", callback_data="quiz_fundamentals")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )

def get_pdf_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 دریافت جزوه اصول و فنون", callback_data="pdf_fundamentals")],
            [InlineKeyboardButton(text="🔙 بازگشت به منوی اصلی ✨", callback_data="back_to_main")]
        ]
    )
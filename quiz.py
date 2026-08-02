from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.inline import back_to_main_menu

router = Router()

class QuizState(StatesGroup):
    active_quiz = State()

@router.callback_query(F.data == "quiz_fundamentals")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🧪 *آزمون اصول و فنون*\n\nاین آزمون در حال ساخت است. لطفاً بعداً مراجعه کنید.",
        reply_markup=back_to_main_menu()
    )
    await callback.answer()
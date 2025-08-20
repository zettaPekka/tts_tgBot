from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from keyboards import user_kbs
from states.user_states import UserState
from database.services.user_service import UserService
from middleware.db_di import DatabaseDI


router = Router()
router.message.middleware(DatabaseDI())

@router.callback_query(F.data == 'deposit')
async def deposit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await callback.message.answer('<b>Пополнение баланса производится через Telegram Stars, введите ниже сумму для пополнения баланса.\n<blockquote>1 ⭐️ - 150 символов</blockquote></b>',
                                        reply_markup=user_kbs.back_kb)
    await state.set_state(UserState.deposit)


@router.message(UserState.deposit)
async def send_check(message: Message, state: FSMContext):
    if message.content_type != ContentType.TEXT or not message.text.isdigit() or int(message.text) > 999999:
        await message.answer('<b>Неверная сумма для пополнения, попробуйте еще раз</b>',
                                reply_markup=user_kbs.back_kb)
        return

    await message.answer_invoice(
        'Пополнение баланса ⭐️',
        'Пополнение баланса для озвучки текста',
        'stars',
        'XTR',
        [LabeledPrice(label='XTR', amount=int(message.text))],
    )
    await state.clear()


@router.pre_checkout_query()
async def checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def star_payment(message: Message, user_service: UserService):
    await user_service.update_balance(message.from_user.id, message.successful_payment.total_amount)
    print(message.successful_payment.total_amount)
    await message.answer(text='<b>Баланс успешно пополнен!🤗</b>')

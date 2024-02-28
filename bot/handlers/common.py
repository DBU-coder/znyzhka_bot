from aiogram import F, Router, types

router = Router()


@router.message(F.text.lower().in_({"metro", "метро", "silpo", "сільпо"}))
async def select_inactive_store(message: types.Message):
    await message.answer(f"Нажаль, магазин {message.text.capitalize()} поки що не доступний.\nВиберить інший магазин.")

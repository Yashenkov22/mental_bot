from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from utils.states import LoadPicture
from db.queries import insert_picture
from utils.keyboards import create_main_kb


pictures_router = Router()


@pictures_router.message(F.text == 'Добавить картинку для коллег')
async def load_picture(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.from_user.id)
    await state.set_state(LoadPicture.pic_id)
    await message.answer('Загрузи фото(одно)')


@pictures_router.message(F.photo)
async def add_picture(message: types.Message,
                      state: FSMContext,
                      session: AsyncSession):
    picture = message.photo[0].file_id

    await state.update_data(pic_id=picture)
    data = await state.get_data()
    await state.clear()
    
    try:
        await insert_picture(session, data)
    except Exception as ex:
        print(ex)
        await message.answer('Не получилось')
    else:
        main_kb = await create_main_kb(data['user_id'], session)
        await message.answer('Фото добавлено',
                             reply_markup=main_kb.as_markup(resize_keyboard=True))
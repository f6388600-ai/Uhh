from aiogram import Router, types
import random

router = Router()

@router.message(lambda m: m.text == "/td")
async def td(msg: types.Message):
    await msg.answer(random.choice(["Truth 😏", "Dare 🔥"]))

def setup():
    return router

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Я AI-агент Holiday Homes по недвижимости в Аланье.")


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer("Агент активен и готов к публикациям.")

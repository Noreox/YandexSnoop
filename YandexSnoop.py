import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, ContentType, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram import Router
from datetime import datetime
import yadisk

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Замените на HTTP-API токен вашего бота
YANDEX_DISK_TOKEN = 'YOUR_YANDEX_DISK_TOKEN'  # Замените на полученный токен вашего приложения

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Инициализация Dispatcher без аргументов
router = Router()

# Инициализация Яндекс.Диска
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)

# Создаем клавиатуру с кнопкой "Очистить корзину"
clear_trash_button = KeyboardButton(text="Очистить корзину")
keyboard = ReplyKeyboardMarkup(keyboard=[[clear_trash_button]], resize_keyboard=True)

async def send_welcome_message():
    chat_id = 'YOUR_CHAT_ID'  # Замените на ваш chat_id
    await bot.send_message(chat_id, "Бот запущен и готов к работе", reply_markup=keyboard)

async def upload_to_yandex_disk(file, file_name):
    folder_name = datetime.now().strftime('%B_%Y')
    if not y.exists(folder_name):
        y.mkdir(folder_name)

    file_path = f"{folder_name}/{file_name}"
    if y.exists(file_path):
        return False  # Файл уже существует

    y.upload(file, file_path)
    return True  # Файл успешно загружен

@router.message(lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_docs(message: types.Message):
    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path
    file_name = document.file_name

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name):
        await message.reply("Файл успешно загружен на Yandex.Disk")
    else:
        await message.reply("Файл уже существует на Yandex.Disk")

@router.message(lambda message: message.content_type == ContentType.PHOTO)
async def handle_photos(message: types.Message):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    file_name = f"{photo.file_id}.jpg"

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name):
        await message.reply("Фото успешно загружено на Yandex.Disk")
    else:
        await message.reply("Фото уже существует на Yandex.Disk")

@router.message(lambda message: message.text == "Очистить корзину")
async def clear_trash(message: types.Message):
    try:
        # Очищаем корзину на Яндекс.Диске
        y.remove_trash("/")
        await message.reply("Корзина успешно очищена", reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Произошла ошибка при очистке корзины: {e}")

# Регистрация роутера
dp.include_router(router)

async def main():
    dp['bot'] = bot  # Устанавливаем bot в Dispatcher
    await send_welcome_message()  # Отправка приветственного сообщения
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
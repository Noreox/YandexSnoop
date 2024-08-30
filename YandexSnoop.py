import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from datetime import datetime
import yadisk
from dotenv import load_dotenv
import os
import requests
import time

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('BOT_API_TOKEN')  # Получение токена бота из переменных окружения
YANDEX_DISK_TOKEN = os.getenv('YANDEX_DISK_TOKEN')  # Получение токена Яндекс.Диска из переменных окружения

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)  # Инициализация Dispatcher с хранилищем состояний
router = Router()

# Инициализация Яндекс.Диска
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)

# Создаем клавиатуру с кнопками "Загрузить файлы", "Очистить корзину" и "Поиск"
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📤Загрузить файлы")],
        [KeyboardButton(text="🗑️Очистить корзину")],
        [KeyboardButton(text="🔎Поиск")]
    ],
    resize_keyboard=True
)

class UploadStates(StatesGroup):
    waiting_for_upload = State()

class SearchStates(StatesGroup):
    waiting_for_query = State()

async def send_welcome_message():
    chat_id = os.getenv('CHAT_ID')  # Получение chat_id из переменных окружения
    await bot.send_message(chat_id, "Бот запущен, чтобы приступить к работе, выберите нужное вам действие", reply_markup=keyboard)

async def upload_to_yandex_disk(file, file_name, folder_type):
    folder_name = datetime.now().strftime('%B_%Y')
    folder_path = f"{folder_name}/{folder_type}"

    if not y.exists(folder_name):
        y.mkdir(folder_name)
    if not y.exists(folder_path):
        y.mkdir(folder_path)

    file_path = f"{folder_path}/{file_name}"
    if y.exists(file_path):
        return False  # Файл уже существует

    y.upload(file, file_path)
    return True  # Файл успешно загружен

@router.message(lambda message: message.text == "📤Загрузить файлы")
async def initiate_upload(message: types.Message, state: FSMContext):
    logging.info("Пользователь нажал кнопку 'Загрузить файлы'")
    await message.reply("Теперь вы можете отправлять файлы и фото для загрузки на Yandex.Disk, для этого выберите нужный тип файла и отправьте его")
    await state.set_state(UploadStates.waiting_for_upload)

@router.message(UploadStates.waiting_for_upload, lambda message: message.content_type == ContentType.DOCUMENT)
async def handle_docs(message: types.Message, state: FSMContext):
    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path
    file_name = document.file_name

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name, "Файлы"):
        await message.reply("Файл успешно загружен на Yandex.Disk в папку 'Файлы'")
    else:
        await message.reply("Файл уже существует на Yandex.Disk")
    await state.clear()

@router.message(UploadStates.waiting_for_upload, lambda message: message.content_type == ContentType.PHOTO)
async def handle_photos(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_path = file_info.file_path
    file_name = f"{photo.file_id}.jpg"

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name, "Фото"):
        await message.reply("Фото успешно загружено на Yandex.Disk в папку 'Фото'")
    else:
        await message.reply("Фото уже существует на Yandex.Disk")
    await state.clear()

@router.message(UploadStates.waiting_for_upload, lambda message: message.content_type == ContentType.VIDEO)
async def handle_videos(message: types.Message, state: FSMContext):
    video = message.video
    file_info = await bot.get_file(video.file_id)
    file_path = file_info.file_path
    file_name = f"{video.file_id}.mp4"

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name, "Видео"):
        await message.reply("Видео успешно загружено на Yandex.Disk в папку 'Видео'")  # Добавлено сообщение об успешной загрузке
    else:
        await message.reply("Видео уже существует на Yandex.Disk")
    await state.clear()

@router.message(UploadStates.waiting_for_upload, lambda message: message.content_type == ContentType.AUDIO)
async def handle_audio(message: types.Message, state: FSMContext):
    audio = message.audio
    file_info = await bot.get_file(audio.file_id)
    file_path = file_info.file_path
    file_name = f"{audio.file_id}.mp3"

    file = await bot.download_file(file_path)

    if await upload_to_yandex_disk(file, file_name, "Музыка"):
        await message.reply("Аудио успешно загружено на Yandex.Disk в папку 'Музыка'")
    else:
        await message.reply("Аудио уже существует на Yandex.Disk")
    await state.clear()

@router.message(lambda message: message.text == "🗑️Очистить корзину")
async def clear_trash(message: types.Message):
    try:
        # Получаем OAuth токен из переменных окружения
        token = os.getenv('YANDEX_DISK_TOKEN')

        # URL для получения информации о корзине
        url_info = "https://cloud-api.yandex.net/v1/disk/trash/resources"

        # Заголовки для авторизации
        headers = {
            "Authorization": f"OAuth {token}"
        }

        # Параметры запроса для получения информации о корзине
        params_info = {
            "path": "/"
        }

        # Отправляем запрос для получения информации о корзине
        response_info = requests.get(url_info, headers=headers, params=params_info)

        if response_info.status_code == 200:
            trash_info = response_info.json()
            if trash_info['_embedded']['total'] == 0:
                await message.reply("Корзина уже пуста", reply_markup=keyboard)
                return
        else:
            await message.reply(f"Произошла ошибка при получении информации о корзине: {response_info.json()}", reply_markup=keyboard)
            return

        # URL для очистки корзины
        url_clear = "https://cloud-api.yandex.net/v1/disk/trash/resources"

        # Параметры запроса для очистки корзины
        params_clear = {
            "path": "/",
            "permanently": "true"
        }

        # Отправляем запрос на очистку корзины
        response_clear = requests.delete(url_clear, headers=headers, params=params_clear)

        if response_clear.status_code == 202:
            operation_href = response_clear.json().get('href')
            # Проверяем статус операции очистки корзины
            while True:
                operation_status = requests.get(operation_href, headers=headers)
                if operation_status.status_code == 200:
                    status = operation_status.json().get('status')
                    if status == 'success':
                        await message.reply("Корзина успешно очищена", reply_markup=keyboard)
                        break
                    elif status == 'failed':
                        await message.reply("Произошла ошибка при очистке корзины", reply_markup=keyboard)
                        break
                time.sleep(1)  # Ждем 1 секунду перед повторной проверкой
        elif response_clear.status_code == 204:
            await message.reply("Корзина успешно очищена", reply_markup=keyboard)
        else:
            await message.reply(f"Произошла ошибка при очистке корзины: {response_clear.json()}", reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Произошла ошибка при очистке корзины: {e}")

def search_files_and_folders_recursive(path, query):
    search_results = []
    for item in y.listdir(path):
        logging.info(f"Проверка элемента: {item['name']} (тип: {item['type']})")
        if item['type'] == 'dir':
            if query.lower() in item['name'].lower():
                search_results.append(item['path'])
            search_results.extend(search_files_and_folders_recursive(item['path'], query))
        elif item['type'] == 'file' and query.lower() in item['name'].lower():
            search_results.append(item['path'])
    return search_results

@router.message(lambda message: message.text == "🔎Поиск")
async def initiate_search(message: types.Message, state: FSMContext):
    logging.info("Пользователь нажал кнопку 'Поиск'")
    await message.reply("Какие файлы или папки вы желаете найти?")
    await state.set_state(SearchStates.waiting_for_query)

@router.message(SearchStates.waiting_for_query)
async def search_files(message: types.Message, state: FSMContext):
    logging.info(f"Получен запрос на поиск: {message.text}")
    query = message.text
    if not query:
        await message.reply("Пожалуйста, укажите критерии поиска.")
        return

    # Реализация рекурсивного поиска файлов и папок
    search_results = search_files_and_folders_recursive("/", query)
    logging.info(f"Результаты поиска для '{query}': {search_results}")

    if not search_results:
        await message.reply("Файлы и папки не найдены.")
    else:
        # Формирование ответа с результатами поиска
        results_message = "\n".join(search_results)
        await message.reply(f"Найденные файлы и папки:\n{results_message}")

    await state.clear()

# Регистрация роутера
dp.include_router(router)

async def main():
    dp['bot'] = bot  # Устанавливаем bot в Dispatcher
    await send_welcome_message()  # Отправка приветственного сообщения
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
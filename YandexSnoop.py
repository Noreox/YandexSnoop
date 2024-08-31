# Импорт необходимых библиотек и модулей
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
from typing import Union, BinaryIO
from functools import wraps

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токенов из переменных окружения
API_TOKEN = os.getenv('TELEGRAM_API_BOT_TOKEN')
YANDEX_DISK_TOKEN = os.getenv('YANDEX_OAUTH_API_APP_ID')
CHAT_ID = os.getenv('CHAT_ID')

if not all([API_TOKEN, YANDEX_DISK_TOKEN, CHAT_ID]):
    raise ValueError("Не все необходимые переменные окружения установлены. Проверьте файл .env")

# Константы для URL-адресов API Яндекс.Диска
YANDEX_DISK_API_BASE_URL = "https://cloud-api.yandex.net/v1/disk"
TRASH_RESOURCES_URL = f"{YANDEX_DISK_API_BASE_URL}/trash/resources"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота, хранилища состояний и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Инициализация клиента Яндекс.Диска
y = yadisk.YaDisk(token=YANDEX_DISK_TOKEN)

# Определение состояний для конечного автомата (FSM)
class BotStates(StatesGroup):
    idle = State()
    uploading = State()
    searching = State()

def is_authorized(message: types.Message) -> bool:
    authorized_chat_id = int(CHAT_ID)
    return message.chat.id == authorized_chat_id

# Декоратор для проверки авторизации
def auth_required(func):
    @wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        if is_authorized(message):
            return await func(message, *args, **kwargs)
        else:
            await message.reply("Вы не авторизованы для использования этого бота.")
    return wrapper

async def send_welcome_message() -> None:
    """Отправляет приветственное сообщение в чат."""
    chat_id = int(CHAT_ID)
    await bot.send_message(chat_id, "Бот запущен, чтобы приступить к работе, выберите нужное вам действие")

async def upload_to_yandex_disk(file: BinaryIO, file_name: str, folder_type: str) -> bool:
    """
    Загружает файл на Яндекс Диск.

    :param file: Файл для загрузки
    :param file_name: Имя файла
    :param folder_type: Тип папки для загрузки
    :return: True, если файл успешно загружен, False, если файл уже существует
    """
    folder_name = datetime.now().strftime('%B_%Y')
    folder_path = f"{folder_name}/{folder_type}"

    try:
        # Создание папок, если они не существуют
        if not y.exists(folder_name):
            y.mkdir(folder_name)
        if not y.exists(folder_path):
            y.mkdir(folder_path)

        file_path = f"{folder_path}/{file_name}"
        if y.exists(file_path):
            return False

        # Загрузка файла
        y.upload(file, file_path)
        return True
    except yadisk.exceptions.YaDiskError as e:
        logging.error(f"Ошибка при загрузке файла на Яндекс.Диск: {e}")
        return False

@router.message(Command(commands=["space_info", "clear", "search", "upload"]))
@auth_required
async def handle_commands(message: types.Message, state: FSMContext) -> None:
    """Обрабатывает все команды и сбрасывает состояние."""
    await state.set_state(BotStates.idle)
    
    if message.text == '/space_info':
        await get_space_info(message, state)
    elif message.text == '/clear':
        await clear_trash(message, state)
    elif message.text == '/search':
        await initiate_search(message, state)
    elif message.text == '/upload':
        await initiate_upload(message, state)

@router.message(Command(commands=["upload"]))
@auth_required
async def initiate_upload(message: types.Message, state: FSMContext) -> None:
    """Инициирует процесс загрузки файла."""
    logging.info("Пользователь ввел команду '/upload'")
    await message.reply("Теперь вы можете отправлять файлы и фото для загрузки на Яндекс Диск, для этого выберите нужный тип файла и отправьте его. Чтобы выйти из режима загрузки, введите любую другую команду.")
    await state.set_state(BotStates.uploading)

async def handle_file_upload(message: types.Message, state: FSMContext, file_type: str) -> None:
    """
    Обрабатывает загрузку файла на Яндекс Диск.

    :param message: Сообщение с файлом
    :param state: Состояние FSM
    :param file_type: Тип файла (document, photo, video, audio)
    """
    file_obj = getattr(message, file_type)
    if file_type == 'photo':
        file_obj = file_obj[-1]  # Берем последнее (самое большое) фото
    file_info = await bot.get_file(file_obj.file_id)
    file_path = file_info.file_path
    file_name = getattr(file_obj, 'file_name', f"{file_obj.file_id}.{file_type}")

    file = await bot.download_file(file_path)

    # Проверка размера файла (ограничение в 100 МБ)
    if file.getbuffer().nbytes > 100 * 1024 * 1024:
        await message.reply(f"{file_type.capitalize()} слишком большой. Максимальный размер - 100 МБ.")
        return

    folder_type = {"document": "Файлы", "photo": "Фото", "video": "Видео", "audio": "Музыка"}[file_type]

    if await upload_to_yandex_disk(file, file_name, folder_type):
        await message.reply(f"{file_type.capitalize()} успешно загружен на Яндекс Диск в папку '{folder_type}'. Вы можете продолжать отправлять файлы или ввести другую команду для выхода из режима загрузки.")
    else:
        await message.reply(f"{file_type.capitalize()} уже существует на Яндекс Диске. Вы можете продолжать отправлять файлы или ввести другую команду для выхода из режима загрузки.")

# Обработчики для различных типов файлов
@router.message(BotStates.uploading, lambda message: message.content_type == ContentType.DOCUMENT)
@auth_required
async def handle_docs(message: types.Message, state: FSMContext) -> None:
    await handle_file_upload(message, state, "document")

@router.message(BotStates.uploading, lambda message: message.content_type == ContentType.PHOTO)
@auth_required
async def handle_photos(message: types.Message, state: FSMContext) -> None:
    await handle_file_upload(message, state, "photo")

@router.message(BotStates.uploading, lambda message: message.content_type == ContentType.VIDEO)
@auth_required
async def handle_videos(message: types.Message, state: FSMContext) -> None:
    await handle_file_upload(message, state, "video")

@router.message(BotStates.uploading, lambda message: message.content_type == ContentType.AUDIO)
@auth_required
async def handle_audio(message: types.Message, state: FSMContext) -> None:
    await handle_file_upload(message, state, "audio")

@router.message(Command(commands=["clear"]))
@auth_required
async def clear_trash(message: types.Message, state: FSMContext) -> None:
    """Очищает корзину Яндекс.Диска."""
    try:
        headers = {"Authorization": f"OAuth {YANDEX_DISK_TOKEN}"}
        params_info = {"path": "/"}

        logging.info(f"Отправка запроса к Яндекс.Диску. URL: {TRASH_RESOURCES_URL}, Headers: {headers}, Params: {params_info}")

        # Получение информации о корзине
        response_info = requests.get(TRASH_RESOURCES_URL, headers=headers, params=params_info)

        logging.info(f"Получен ответ от Яндекс.Диска. Статус: {response_info.status_code}, Тело: {response_info.text}")

        if response_info.status_code == 200:
            trash_info = response_info.json()
            if trash_info['_embedded']['total'] == 0:
                await message.reply("Корзина уже пуста")
                return
        else:
            await message.reply(f"Произошла ошибка при получении информации о корзине: {response_info.json()}")
            return

        # Очистка корзины
        params_clear = {"path": "/", "permanently": "true"}
        response_clear = requests.delete(TRASH_RESOURCES_URL, headers=headers, params=params_clear)

        if response_clear.status_code == 202:
            operation_href = response_clear.json().get('href')
            # Ожидание завершения операции очистки
            while True:
                operation_status = requests.get(operation_href, headers=headers)
                if operation_status.status_code == 200:
                    status = operation_status.json().get('status')
                    if status == 'success':
                        await message.reply("Корзина успешно очищена")
                        break
                    elif status == 'failed':
                        await message.reply("Произошла ошибка при очистке корзины")
                        break
                time.sleep(1)
        elif response_clear.status_code == 204:
            await message.reply("Корзина успешно очищена")
        else:
            await message.reply(f"Произошла ошибка при очистке корзины: {response_clear.json()}")
    except Exception as e:
        await message.reply(f"Произошла ошибка при очистке корзины: {e}")

def search_files_and_folders_recursive(path: str, query: str) -> list:
    """
    Рекурсивно ищет файлы и папки на Яндекс.Диске.

    :param path: Путь для поиска
    :param query: Поисковый запрос
    :return: Список найденных файлов и папок
    """
    search_results = []
    for item in y.listdir(path):
        logging.info(f"Проверка элемента: {item['name']} (тип: {item['type']})")
        if item['type'] == 'dir':
            if query.lower() in item['name'].lower():
                search_results.append(item['path'])
            # Рекурсивный поиск в подпапках
            search_results.extend(search_files_and_folders_recursive(item['path'], query))
        elif item['type'] == 'file' and query.lower() in item['name'].lower():
            search_results.append(item['path'])
    return search_results

@router.message(Command(commands=["search"]))
@auth_required
async def initiate_search(message: types.Message, state: FSMContext) -> None:
    """Инициирует процесс поиска файлов и папок."""
    logging.info("Пользователь ввел команду '/search'")
    await message.reply("Введите запрос для поиска файлов или папок. Чтобы выйти из режима поиска, введите любую другую команду.")
    await state.set_state(BotStates.searching)

@router.message(BotStates.searching)
@auth_required
async def search_files(message: types.Message, state: FSMContext) -> None:
    """Выполняет поиск файлов и папок на Яндекс.Диске."""
    if message.text.startswith('/'):
        # Если введена команда, выходим из режима поиска
        return

    logging.info(f"Получен запрос на поиск: {message.text}")
    query = message.text
    if not query:
        await message.reply("Пожалуйста, укажите критерии поиска.")
        return

    search_results = search_files_and_folders_recursive("/", query)
    logging.info(f"Результаты поиска для '{query}': {search_results}")

    if not search_results:
        await message.reply("Файлы и папки с таким содержимым не найдены. Вы можете продолжить поиск, введя новый запрос, или ввести другую команду для выхода из режима поиска.")
    else:
        results_message = "\n".join(search_results)
        await message.reply(f"Найденные файлы и папки:\n{results_message}\n\nВы можете продолжить поиск, введя новый запрос, или ввести другую команду для выхода из режима поиска.")

@router.message(Command(commands=["space_info"]))
@auth_required
async def get_space_info(message: types.Message, state: FSMContext) -> None:
    """Получает информацию о свободном месте на Яндекс.Диске."""
    try:
        disk_info = y.get_disk_info()
        total_space = disk_info['total_space']
        used_space = disk_info['used_space']
        free_space = total_space - used_space

        # Конвертация байтов в гигабайты
        total_space_gb = total_space / (1024 ** 3)
        used_space_gb = used_space / (1024 ** 3)
        free_space_gb = free_space / (1024 ** 3)

        response = (
            f"Информация о пространстве на Яндекс.Диске:\n"
            f"Общее пространство: {total_space_gb:.2f} ГБ\n"
            f"Использовано: {used_space_gb:.2f} ГБ\n"
            f"Свободно: {free_space_gb:.2f} ГБ"
        )
        await message.reply(response)
    except Exception as e:
        logging.error(f"Ошибка при получении информации о пространстве: {e}")
        await message.reply("Произошла ошибка при получении информации о пространстве на Яндекс.Диске.")

# Регистрация роутера
dp.include_router(router)

async def main() -> None:
    """Основная функция для запуска бота."""
    await send_welcome_message() 
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())